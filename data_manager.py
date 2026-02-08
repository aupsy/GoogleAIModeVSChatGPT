"""
Data Manager Module
Handles all data persistence operations including loading queries,
saving responses, tracking progress, and managing results.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import shutil

# File paths
QUERY_FILE = 'query_dataset.json'
RESULTS_FILE = 'results.json'
PROGRESS_FILE = 'progress.json'


def load_queries() -> List[Dict]:
    """
    Load all queries from the dataset file.

    Returns:
        List of query dictionaries with id, query, category, quality, intent_clarity
    """
    try:
        with open(QUERY_FILE, 'r', encoding='utf-8') as f:
            queries = json.load(f)

        # Add sequential IDs if not present
        for idx, query in enumerate(queries):
            if 'id' not in query:
                query['id'] = idx

        return queries
    except FileNotFoundError:
        print(f"Error: {QUERY_FILE} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing {QUERY_FILE}: {e}")
        return []


def load_results() -> Dict:
    """
    Load existing results from results.json.
    Creates empty structure if file doesn't exist.

    Returns:
        Dictionary mapping query_id to response data
    """
    if not os.path.exists(RESULTS_FILE):
        return {}

    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Backup corrupted file and start fresh
        backup_file(RESULTS_FILE)
        return {}


def load_progress() -> Dict:
    """
    Load progress tracking data.

    Returns:
        Dictionary mapping query_id to completion status
        Format: {
            query_id: {
                'chatgpt_done': bool,
                'google_done': bool,
                'scored': bool,
                'last_updated': timestamp
            }
        }
    """
    if not os.path.exists(PROGRESS_FILE):
        return {}

    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        backup_file(PROGRESS_FILE)
        return {}


def save_result(query_id: int, platform: str, response_data: Dict) -> bool:
    """
    Save a response for a specific query and platform.

    Args:
        query_id: ID of the query
        platform: 'chatgpt' or 'google'
        response_data: Dictionary containing response text, timestamp, etc.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load existing results
        results = load_results()

        # Initialize query entry if doesn't exist
        if str(query_id) not in results:
            results[str(query_id)] = {
                'query_id': query_id,
                'chatgpt': None,
                'google': None,
                'scores': None
            }

        # Add timestamp if not present
        if 'timestamp' not in response_data:
            response_data['timestamp'] = datetime.now().isoformat()

        # Save response
        results[str(query_id)][platform] = response_data

        # Backup before writing
        if os.path.exists(RESULTS_FILE):
            backup_file(RESULTS_FILE)

        # Write to file
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Update progress
        update_progress(query_id, f'{platform}_done')

        return True

    except Exception as e:
        print(f"Error saving result: {e}")
        return False


def save_scores(query_id: int, scores: Dict) -> bool:
    """
    Save evaluation scores for a query.

    Args:
        query_id: ID of the query
        scores: Dictionary containing relevance, completeness, source_quality, etc.

    Returns:
        True if successful, False otherwise
    """
    try:
        results = load_results()

        if str(query_id) not in results:
            print(f"Error: Query {query_id} not found in results")
            return False

        # Add timestamp
        scores['timestamp'] = datetime.now().isoformat()

        # Save scores
        results[str(query_id)]['scores'] = scores

        # Backup before writing
        if os.path.exists(RESULTS_FILE):
            backup_file(RESULTS_FILE)

        # Write to file
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Update progress
        update_progress(query_id, 'scored')

        return True

    except Exception as e:
        print(f"Error saving scores: {e}")
        return False


def update_progress(query_id: int, status_field: str) -> bool:
    """
    Update progress tracking for a query.

    Args:
        query_id: ID of the query
        status_field: Field to mark as complete ('chatgpt_done', 'google_done', 'scored')

    Returns:
        True if successful, False otherwise
    """
    try:
        progress = load_progress()

        # Initialize query progress if doesn't exist
        if str(query_id) not in progress:
            progress[str(query_id)] = {
                'chatgpt_done': False,
                'google_done': False,
                'scored': False,
                'last_updated': None
            }

        # Update status
        progress[str(query_id)][status_field] = True
        progress[str(query_id)]['last_updated'] = datetime.now().isoformat()

        # Write to file
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Error updating progress: {e}")
        return False


def get_next_batch(batch_size: int = 20) -> List[Dict]:
    """
    Get the next batch of incomplete queries.

    Args:
        batch_size: Number of queries to return

    Returns:
        List of query dictionaries that need work
    """
    queries = load_queries()
    progress = load_progress()

    incomplete = []
    for query in queries:
        query_id = str(query['id'])
        query_progress = progress.get(query_id, {})

        # Check if query needs any work
        if not (query_progress.get('chatgpt_done', False) and
                query_progress.get('google_done', False) and
                query_progress.get('scored', False)):
            incomplete.append(query)

        if len(incomplete) >= batch_size:
            break

    return incomplete


def get_queries_needing_chatgpt(batch_size: int = 20) -> List[Dict]:
    """Get queries that need ChatGPT responses."""
    queries = load_queries()
    progress = load_progress()

    needed = []
    for query in queries:
        query_id = str(query['id'])
        if not progress.get(query_id, {}).get('chatgpt_done', False):
            needed.append(query)

        if len(needed) >= batch_size:
            break

    return needed


def get_queries_needing_google(batch_size: int = 20) -> List[Dict]:
    """Get queries that need Google AI Mode responses."""
    queries = load_queries()
    progress = load_progress()

    needed = []
    for query in queries:
        query_id = str(query['id'])
        if not progress.get(query_id, {}).get('google_done', False):
            needed.append(query)

        if len(needed) >= batch_size:
            break

    return needed


def get_queries_needing_scores() -> List[Dict]:
    """Get queries that have both responses but no scores."""
    queries = load_queries()
    progress = load_progress()
    results = load_results()

    needed = []
    for query in queries:
        query_id = str(query['id'])
        query_progress = progress.get(query_id, {})

        # Check if both responses exist but not scored
        if (query_progress.get('chatgpt_done', False) and
            query_progress.get('google_done', False) and
            not query_progress.get('scored', False)):

            # Add the responses to the query object
            if query_id in results:
                query['chatgpt_response'] = results[query_id].get('chatgpt')
                query['google_response'] = results[query_id].get('google')

            needed.append(query)

    return needed


def get_completion_stats() -> Dict:
    """
    Get statistics about completion status.

    Returns:
        Dictionary with completion counts and percentages
    """
    queries = load_queries()
    total = len(queries)

    # Load results to count actual responses and scores (including LLM scores)
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except Exception as e:
        print(f"ERROR loading results: {e}")
        results = {}

    chatgpt_done = 0
    google_done = 0
    scored = 0
    fully_complete = 0

    for qid_str in results:
        has_chatgpt = bool(results[qid_str].get('chatgpt'))
        has_google = bool(results[qid_str].get('google'))
        has_scores = bool(results[qid_str].get('scores') or results[qid_str].get('llm_scores'))

        if has_chatgpt:
            chatgpt_done += 1
        if has_google:
            google_done += 1
        if has_scores:
            scored += 1
        if has_chatgpt and has_google and has_scores:
            fully_complete += 1

    return {
        'total_queries': total,
        'chatgpt_responses': chatgpt_done,
        'google_responses': google_done,
        'scored': scored,
        'fully_complete': fully_complete,
        'percent_complete': (fully_complete / total * 100) if total > 0 else 0
    }


def backup_file(filepath: str) -> None:
    """Create a timestamped backup of a file."""
    if not os.path.exists(filepath):
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"

    try:
        shutil.copy2(filepath, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")


def reset_progress() -> bool:
    """Reset all progress (use with caution!)."""
    try:
        if os.path.exists(PROGRESS_FILE):
            backup_file(PROGRESS_FILE)
            os.remove(PROGRESS_FILE)
        return True
    except Exception as e:
        print(f"Error resetting progress: {e}")
        return False


if __name__ == "__main__":
    # Test the module
    print("Testing data_manager.py...")

    queries = load_queries()
    print(f"Loaded {len(queries)} queries")

    if queries:
        print(f"First query: {queries[0]}")

    stats = get_completion_stats()
    print(f"\nCompletion stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
