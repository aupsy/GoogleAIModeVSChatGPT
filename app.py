"""
Flask Web Application
Main web server providing API and UI for the evaluation tool.
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import os
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

import data_manager
import chatgpt_client
import analyzer
import report_generator
import sampling

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Global state for batch processing
batch_processing = {
    'running': False,
    'progress': 0,
    'total': 0,
    'current_query': None,
    'errors': [],
    'success_count': 0,
    'completed': False,
    'completion_message': None
}

# Manual scoring sample
manual_scoring_sample = {
    'generated': False,
    'sample_ids': [],
    'sample_size': 20
}


@app.route('/')
def index():
    """Serve the main interface."""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current completion status."""
    try:
        stats = data_manager.get_completion_stats()

        # Add batch processing status
        stats['batch_processing'] = {
            'running': batch_processing['running'],
            'progress': batch_processing['progress'],
            'total': batch_processing['total'],
            'current_query': batch_processing['current_query'],
            'completed': batch_processing['completed'],
            'success_count': batch_processing['success_count'],
            'completion_message': batch_processing['completion_message'],
            'error_count': len(batch_processing['errors']),
            'errors': batch_processing['errors'][:3]  # Only send first 3 errors to avoid huge payloads
        }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/next-batch')
def get_next_batch():
    """Get the next batch of queries to work on."""
    try:
        batch_size = request.args.get('size', 20, type=int)

        # Get queries needing work
        next_batch = data_manager.get_next_batch(batch_size)

        return jsonify({
            'success': True,
            'queries': next_batch,
            'count': len(next_batch)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/queries-needing-google')
def get_queries_needing_google():
    """Get queries that need Google AI responses."""
    try:
        batch_size = request.args.get('size', 1, type=int)
        queries = data_manager.get_queries_needing_google(batch_size)

        return jsonify({
            'success': True,
            'queries': queries,
            'count': len(queries)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/queries-needing-scores')
def get_queries_needing_scores():
    """Get queries that need scoring."""
    try:
        queries = data_manager.get_queries_needing_scores()

        # If manual sample is generated, only show queries from the sample
        if manual_scoring_sample['generated'] and manual_scoring_sample['sample_ids']:
            queries = [q for q in queries if q['id'] in manual_scoring_sample['sample_ids']]

        # Limit to first 5 for UI display
        display_queries = queries[:5]

        return jsonify({
            'success': True,
            'queries': display_queries,
            'total_needing_scores': len(queries),
            'manual_sample_active': manual_scoring_sample['generated']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/run-chatgpt-batch', methods=['POST'])
def run_chatgpt_batch():
    """Run a batch of ChatGPT queries."""
    if batch_processing['running']:
        return jsonify({
            'success': False,
            'error': 'Batch already running'
        }), 400

    try:
        data = request.get_json()
        batch_size = data.get('batch_size', 20)

        # Clear previous completion status
        batch_processing['completed'] = False
        batch_processing['completion_message'] = None
        batch_processing['errors'] = []
        batch_processing['success_count'] = 0

        # Get queries needing ChatGPT responses
        queries_to_process = data_manager.get_queries_needing_chatgpt(batch_size)

        if not queries_to_process:
            return jsonify({
                'success': True,
                'message': 'No queries need ChatGPT responses',
                'processed': 0
            })

        # Run batch in background thread
        thread = Thread(
            target=process_chatgpt_batch,
            args=(queries_to_process,)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'message': f'Started processing {len(queries_to_process)} queries',
            'count': len(queries_to_process)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/acknowledge-batch', methods=['POST'])
def acknowledge_batch():
    """Acknowledge batch completion message."""
    batch_processing['completed'] = False
    batch_processing['completion_message'] = None
    return jsonify({'success': True})


def process_chatgpt_batch(queries):
    """Background function to process ChatGPT batch."""
    global batch_processing

    batch_processing['running'] = True
    batch_processing['progress'] = 0
    batch_processing['total'] = len(queries)
    batch_processing['errors'] = []
    batch_processing['success_count'] = 0
    batch_processing['completed'] = False
    batch_processing['completion_message'] = None

    try:
        # Initialize ChatGPT client
        client = chatgpt_client.ChatGPTClient()

        # Process each query
        def progress_callback(current, total, query_id, result):
            batch_processing['progress'] = current
            batch_processing['current_query'] = f"Query {query_id}"

            # Save result
            if result:
                data_manager.save_result(query_id, 'chatgpt', result)
                batch_processing['success_count'] += 1

        # Run batch
        results = client.batch_query(queries, callback=progress_callback)

        # Count successes and failures
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]

        batch_processing['success_count'] = len(successful)
        batch_processing['errors'] = failed

        # Generate completion message
        if len(failed) == 0:
            batch_processing['completion_message'] = f"SUCCESS: Successfully processed all {len(successful)} queries!"
        elif len(successful) == 0:
            batch_processing['completion_message'] = f"FAILED: All {len(queries)} queries failed. Please check your API key and billing."
        else:
            batch_processing['completion_message'] = f"PARTIAL: {len(successful)} succeeded, {len(failed)} failed."

    except Exception as e:
        error_msg = format_error_message(str(e))
        batch_processing['errors'].append({'error': error_msg})
        batch_processing['completion_message'] = f"FAILED: Batch failed - {error_msg}"
        print(f"Error in batch processing: {e}")

    finally:
        batch_processing['running'] = False
        batch_processing['current_query'] = None
        batch_processing['completed'] = True


def format_error_message(error_str):
    """Convert API errors to human-readable messages."""
    error_lower = error_str.lower()

    # Check for common error types
    if 'insufficient_quota' in error_lower or 'quota' in error_lower:
        return "API quota exceeded. Please check your OpenAI billing at platform.openai.com/account/billing"
    elif 'authentication' in error_lower or 'api key' in error_lower:
        return "Invalid API key. Please check your .env file and update OPENAI_API_KEY"
    elif 'rate_limit' in error_lower or 'rate limit' in error_lower:
        return "Rate limit exceeded. Too many requests. Please wait and try again."
    elif 'timeout' in error_lower:
        return "Request timeout. Check your internet connection and try again."
    elif 'connection' in error_lower or 'network' in error_lower:
        return "Network error. Check your internet connection."
    elif 'model' in error_lower and 'not found' in error_lower:
        return "Invalid model specified. Check config.json for the correct model name."
    else:
        return error_str


@app.route('/api/save-google-response', methods=['POST'])
def save_google_response():
    """Save a Google AI Mode response."""
    try:
        data = request.get_json()

        query_id = data.get('query_id')
        response_text = data.get('response')
        response_time_ms = data.get('response_time_ms')

        if query_id is None or not response_text:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # Save response
        response_data = {
            'response': response_text,
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': response_time_ms
        }

        success = data_manager.save_result(query_id, 'google', response_data)

        return jsonify({
            'success': success,
            'message': 'Response saved'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/save-scores', methods=['POST'])
def save_scores():
    """Save evaluation scores for a query."""
    try:
        data = request.get_json()

        query_id = data.get('query_id')
        scores = data.get('scores')

        if query_id is None or not scores:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # Validate scores
        required_fields = [
            'chatgpt_relevance', 'chatgpt_completeness', 'chatgpt_source_quality',
            'google_relevance', 'google_completeness', 'google_source_quality',
            'chatgpt_intent_understood', 'google_intent_understood'
        ]

        for field in required_fields:
            if field not in scores:
                return jsonify({
                    'success': False,
                    'error': f'Missing score field: {field}'
                }), 400

        # Save scores
        success = data_manager.save_scores(query_id, scores)

        return jsonify({
            'success': success,
            'message': 'Scores saved'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics')
def get_statistics():
    """Get current statistical analysis."""
    try:
        analysis = analyzer.generate_full_analysis()

        if 'error' in analysis:
            return jsonify({
                'success': False,
                'error': analysis['error']
            })

        # Add insights
        insights = analyzer.generate_insights(analysis)
        analysis['insights'] = insights

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export')
def export_report():
    """Generate and download Excel report."""
    try:
        # Generate report
        output_file = report_generator.create_excel_report()

        if not output_file:
            return jsonify({
                'success': False,
                'error': 'Failed to generate report'
            }), 500

        # Send file
        return send_file(
            output_file,
            as_attachment=True,
            download_name=output_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration."""
    if request.method == 'GET':
        try:
            with open('config.json', 'r') as f:
                config_data = json.load(f)

            return jsonify({
                'success': True,
                'config': config_data
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    else:  # POST
        try:
            new_config = request.get_json()

            # Validate
            if 'batch_size' in new_config:
                if not (1 <= new_config['batch_size'] <= 100):
                    return jsonify({
                        'success': False,
                        'error': 'Batch size must be between 1 and 100'
                    }), 400

            # Update config
            with open('config.json', 'w') as f:
                json.dump(new_config, f, indent=2)

            return jsonify({
                'success': True,
                'message': 'Configuration updated'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/query/<int:query_id>')
def get_query_detail(query_id):
    """Get detailed information about a specific query."""
    try:
        queries = data_manager.load_queries()
        results = data_manager.load_results()

        # Find query
        query = next((q for q in queries if q['id'] == query_id), None)

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404

        # Get results if available
        query_results = results.get(str(query_id), {})

        return jsonify({
            'success': True,
            'query': query,
            'results': query_results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-manual-sample', methods=['POST'])
def generate_manual_sample():
    """Generate a stratified sample of queries for manual scoring."""
    global manual_scoring_sample

    try:
        # Check if we have enough responses
        stats = data_manager.get_completion_stats()

        min_responses = 50  # At least 50 of each type
        if stats['chatgpt_responses'] < min_responses or stats['google_responses'] < min_responses:
            return jsonify({
                'success': False,
                'error': f'Need at least {min_responses} responses from each platform. Current: ChatGPT={stats["chatgpt_responses"]}, Google={stats["google_responses"]}',
                'ready': False
            }), 400

        # Get queries that have both responses
        queries_with_both = data_manager.get_queries_needing_scores()

        if len(queries_with_both) < 20:
            return jsonify({
                'success': False,
                'error': f'Need at least 20 queries with both responses. Current: {len(queries_with_both)}',
                'ready': False
            }), 400

        # Generate stratified sample
        sample = sampling.select_stratified_sample(queries_with_both, sample_size=20)

        # Store sample IDs
        manual_scoring_sample['generated'] = True
        manual_scoring_sample['sample_ids'] = [q['id'] for q in sample]

        # Get distribution
        distribution = sampling.get_sample_distribution(sample)

        return jsonify({
            'success': True,
            'message': f'Generated sample of {len(sample)} queries for manual scoring',
            'sample_size': len(sample),
            'sample_ids': manual_scoring_sample['sample_ids'],
            'distribution': distribution
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/manual-sample-status')
def manual_sample_status():
    """Get status of manual scoring sample."""
    try:
        stats = data_manager.get_completion_stats()
        queries_with_both = data_manager.get_queries_needing_scores()

        min_responses = 50
        ready = (stats['chatgpt_responses'] >= min_responses and
                 stats['google_responses'] >= min_responses and
                 len(queries_with_both) >= 20)

        return jsonify({
            'success': True,
            'generated': manual_scoring_sample['generated'],
            'sample_ids': manual_scoring_sample['sample_ids'],
            'sample_size': manual_scoring_sample['sample_size'],
            'ready_to_generate': ready,
            'chatgpt_responses': stats['chatgpt_responses'],
            'google_responses': stats['google_responses'],
            'queries_with_both': len(queries_with_both)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auto-score-remaining', methods=['POST'])
def auto_score_remaining():
    """Automatically score remaining unscored queries using LLM-as-judge."""
    try:
        from llm_judge import LLMJudge

        # Get queries that need scoring
        queries_to_score = data_manager.get_queries_needing_scores()

        if not queries_to_score:
            return jsonify({
                'success': True,
                'message': 'No queries need scoring',
                'scored': 0
            })

        # Initialize judge
        judge = LLMJudge()

        # Score each query
        scored_count = 0
        errors = []

        for query in queries_to_score:
            try:
                query_id = query['id']
                chatgpt_resp = query.get('chatgpt_response', {}).get('response', '')
                google_resp = query.get('google_response', {}).get('response', '')

                if not chatgpt_resp or not google_resp:
                    continue

                # Get metadata
                metadata = {
                    'category': query.get('category', ''),
                    'quality': query.get('quality', ''),
                    'intent_clarity': query.get('intent_clarity', '')
                }

                # Evaluate both responses
                evaluations = judge.compare_responses(
                    query['query'],
                    chatgpt_resp,
                    google_resp,
                    metadata
                )

                if evaluations['chatgpt'] and evaluations['google']:
                    # Format scores for saving
                    scores = {
                        'chatgpt_relevance': evaluations['chatgpt']['relevance'],
                        'chatgpt_completeness': evaluations['chatgpt']['completeness'],
                        'chatgpt_source_quality': evaluations['chatgpt']['source_quality'],
                        'chatgpt_intent_understood': evaluations['chatgpt']['intent_understood'],
                        'chatgpt_followups_needed': evaluations['chatgpt']['followups_needed'],

                        'google_relevance': evaluations['google']['relevance'],
                        'google_completeness': evaluations['google']['completeness'],
                        'google_source_quality': evaluations['google']['source_quality'],
                        'google_intent_understood': evaluations['google']['intent_understood'],
                        'google_followups_needed': evaluations['google']['followups_needed'],

                        'notes': f"Auto-scored by LLM Judge. ChatGPT: {evaluations['chatgpt'].get('reasoning', '')} | Google: {evaluations['google'].get('reasoning', '')}",
                        'auto_scored': True
                    }

                    # Save scores
                    data_manager.save_scores(query_id, scores)
                    scored_count += 1

            except Exception as e:
                errors.append(f"Query {query_id}: {str(e)}")
                continue

        return jsonify({
            'success': True,
            'message': f'Auto-scored {scored_count} queries',
            'scored': scored_count,
            'errors': errors[:5]  # Only first 5 errors
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("WARNING: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        print("or set the OPENAI_API_KEY environment variable")
        print()

    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"\n{'='*50}")
    print("AI Evaluation Tool")
    print(f"{'='*50}\n")
    print(f"Starting server on http://localhost:{port}")
    print(f"Press Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
