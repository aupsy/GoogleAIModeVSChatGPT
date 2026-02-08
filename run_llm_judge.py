"""
Run LLM Judge on Remaining Queries
Automatically scores all queries with both ChatGPT and Google responses.
"""

import json
from llm_judge import LLMJudge
import time
from datetime import datetime


def run_llm_judge_on_remaining():
    """Run LLM judge on all queries that need automated scoring."""

    print("="*60)
    print("LLM Judge - Automated Scoring")
    print("="*60)
    print()

    # Initialize LLM judge
    try:
        judge = LLMJudge()
        print("[OK] LLM judge initialized")
    except Exception as e:
        print(f"[FAIL] Could not initialize LLM judge: {e}")
        return

    # Load results data
    try:
        with open('results.json', 'r', encoding='utf-8') as f:
            results_data = json.load(f)
        print(f"[OK] Loaded results.json")
    except Exception as e:
        print(f"[FAIL] Could not load results.json: {e}")
        return

    # Load query dataset for metadata
    try:
        with open('query_dataset.json', 'r', encoding='utf-8') as f:
            query_dataset = json.load(f)
        print(f"[OK] Loaded query_dataset.json")
    except Exception as e:
        print(f"[FAIL] Could not load query_dataset.json: {e}")
        return

    # Find queries that need LLM scoring
    queries_to_score = []
    manually_scored_count = 0

    for query_id, data in results_data.items():
        # Skip if no responses
        if not data.get('chatgpt') or not data.get('google'):
            continue

        # Skip if manually scored (keep manual scores)
        if data.get('scores'):
            manually_scored_count += 1
            continue

        # Skip if already has LLM scores
        if data.get('llm_scores'):
            continue

        # Add to list for scoring
        query_info = query_dataset[int(query_id)]
        queries_to_score.append({
            'id': int(query_id),
            'query': query_info['query'],
            'category': query_info['category'],
            'quality': query_info['quality'],
            'intent_clarity': query_info['intent_clarity'],
            'chatgpt_response': data['chatgpt']['response'],
            'google_response': data['google']['response']
        })

    print(f"[OK] Found {manually_scored_count} manually scored queries (keeping those)")
    print(f"[OK] Found {len(queries_to_score)} queries needing LLM scoring")
    print()

    if not queries_to_score:
        print("No queries need scoring!")
        return

    # Estimate cost and time
    cost_estimate = judge.estimate_cost(len(queries_to_score))
    print("COST ESTIMATE:")
    print(f"  Queries to score: {cost_estimate['num_queries']}")
    print(f"  Total evaluations: {cost_estimate['total_evaluations']}")
    print(f"  Estimated cost: ${cost_estimate['estimated_cost_usd']}")
    print(f"  Estimated time: {cost_estimate['estimated_time_minutes']} minutes")
    print()

    # Confirm before proceeding
    print("Starting automated scoring...")
    print("-" * 60)

    start_time = time.time()
    successful = 0
    failed = 0

    for i, query in enumerate(queries_to_score, 1):
        print(f"\n[{i}/{len(queries_to_score)}] Query {query['id']}: {query['query'][:50]}...")

        # Get query metadata
        metadata = {
            'category': query['category'],
            'quality': query['quality'],
            'intent_clarity': query['intent_clarity']
        }

        # Run LLM judge
        try:
            llm_eval = judge.compare_responses(
                query['query'],
                query['chatgpt_response'],
                query['google_response'],
                metadata
            )

            if llm_eval and llm_eval['chatgpt'] and llm_eval['google']:
                # Save LLM scores to results
                query_id_str = str(query['id'])
                if query_id_str not in results_data:
                    print(f"  [WARN] Query {query_id_str} not in results_data")
                    continue

                results_data[query_id_str]['llm_scores'] = {
                    'chatgpt_relevance': llm_eval['chatgpt']['relevance'],
                    'chatgpt_completeness': llm_eval['chatgpt']['completeness'],
                    'chatgpt_source_quality': llm_eval['chatgpt']['source_quality'],
                    'chatgpt_intent_understood': llm_eval['chatgpt']['intent_understood'],
                    'chatgpt_followups_needed': llm_eval['chatgpt']['followups_needed'],
                    'google_relevance': llm_eval['google']['relevance'],
                    'google_completeness': llm_eval['google']['completeness'],
                    'google_source_quality': llm_eval['google']['source_quality'],
                    'google_intent_understood': llm_eval['google']['intent_understood'],
                    'google_followups_needed': llm_eval['google']['followups_needed'],
                    'timestamp': datetime.now().isoformat(),
                    'model': judge.model
                }

                print(f"  [OK] Scored - ChatGPT avg: {(llm_eval['chatgpt']['relevance'] + llm_eval['chatgpt']['completeness'] + llm_eval['chatgpt']['source_quality'])/3:.1f}, "
                      f"Google avg: {(llm_eval['google']['relevance'] + llm_eval['google']['completeness'] + llm_eval['google']['source_quality'])/3:.1f}")
                successful += 1

                # Save after each successful scoring (for safety)
                if successful % 5 == 0:
                    with open('results.json', 'w', encoding='utf-8') as f:
                        json.dump(results_data, f, indent=2, ensure_ascii=False)
                    print(f"  [SAVE] Progress saved ({successful}/{len(queries_to_score)})")

            else:
                print(f"  [FAIL] LLM evaluation returned None")
                failed += 1

        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            failed += 1

        # Rate limiting - small delay between requests
        if i < len(queries_to_score):
            time.sleep(0.5)

    # Save final results
    try:
        with open('results.json', 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        print("\n[OK] Final results saved to results.json")
    except Exception as e:
        print(f"\n[FAIL] Could not save results: {e}")

    # Summary
    elapsed_time = time.time() - start_time
    print()
    print("="*60)
    print("SCORING COMPLETE")
    print("="*60)
    print(f"Total queries processed: {len(queries_to_score)}")
    print(f"Successfully scored: {successful}")
    print(f"Failed: {failed}")
    print(f"Time elapsed: {elapsed_time/60:.1f} minutes")
    print()
    print(f"Manual scores: {manually_scored_count} queries")
    print(f"LLM scores: {successful} queries")
    print(f"Total scored: {manually_scored_count + successful} queries")
    print()
    print("="*60)
    print("Next step: Export final report with all scores!")
    print("="*60)


if __name__ == "__main__":
    run_llm_judge_on_remaining()
