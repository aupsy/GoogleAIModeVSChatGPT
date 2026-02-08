"""
Migration Script: Add web_search_used field to existing ChatGPT responses
Inspects response content to infer whether web search was used.
"""

import json
import re
from datetime import datetime
import shutil

def detect_web_search_from_content(response_text):
    """
    Detect if web search was likely used based on response content.

    Looks for citation patterns like:
    - (domain.com)
    - [domain.com]
    - According to [source]...
    - URL patterns

    Returns:
        tuple: (web_search_used: bool, citation_count: int)
    """
    if not response_text:
        return False, 0

    # Pattern 1: Inline domain citations like (axios.com) or [axios.com]
    domain_pattern = r'[\(\[]([a-zA-Z0-9-]+\.[a-zA-Z]{2,})[\)\]]'
    domain_matches = re.findall(domain_pattern, response_text)

    # Pattern 2: Full URLs
    url_pattern = r'https?://[^\s\)\]"]+'
    url_matches = re.findall(url_pattern, response_text)

    # Pattern 3: Citation markers (common in web search responses)
    # Like "According to X," or "Source: Y"
    citation_markers = [
        r'according to [^,\.]+,',
        r'source: [^,\.]+',
        r'\[source\]',
        r'as reported by [^,\.]+',
    ]
    marker_matches = sum([len(re.findall(pattern, response_text, re.IGNORECASE))
                         for pattern in citation_markers])

    total_citations = len(domain_matches) + len(url_matches) + marker_matches
    web_search_used = total_citations > 0

    return web_search_used, total_citations


def migrate_results():
    """
    Migrate results.json to add web_search_used fields to existing entries.
    Creates a backup before modifying.
    """
    results_file = 'results.json'

    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'results.json.backup_{timestamp}'
    shutil.copy(results_file, backup_file)
    print(f"Created backup: {backup_file}")

    # Load existing results
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    print(f"\nMigrating {len(results)} queries...")

    updated_count = 0
    inferred_yes = 0
    inferred_no = 0

    for query_id, data in results.items():
        if 'chatgpt' in data and data['chatgpt']:
            chatgpt_data = data['chatgpt']

            # Check if field already exists
            if 'web_search_used' not in chatgpt_data:
                # Infer from response content
                response_text = chatgpt_data.get('response', '')
                web_search_used, citation_count = detect_web_search_from_content(response_text)

                # Add fields
                chatgpt_data['web_search_used'] = web_search_used
                chatgpt_data['web_search_citations_count'] = citation_count

                updated_count += 1
                if web_search_used:
                    inferred_yes += 1
                    print(f"  Query {query_id}: Web search = YES ({citation_count} citations)")
                else:
                    inferred_no += 1

    # Save updated results
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nMigration complete!")
    print(f"  Updated entries: {updated_count}")
    print(f"  Inferred YES (web search used): {inferred_yes}")
    print(f"  Inferred NO (no web search): {inferred_no}")
    print(f"\nBackup saved to: {backup_file}")
    print(f"Updated results saved to: {results_file}")


def verify_migration():
    """Verify the migration by showing some examples."""
    with open('results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

    print("\n=== Verification Sample ===\n")

    # Show a few examples
    count = 0
    for query_id, data in results.items():
        if 'chatgpt' in data and data['chatgpt'] and count < 5:
            chatgpt = data['chatgpt']
            if 'web_search_used' in chatgpt:
                print(f"Query {query_id}:")
                print(f"  Model: {chatgpt.get('model', 'N/A')}")
                print(f"  Web Search Used: {chatgpt['web_search_used']}")
                print(f"  Citation Count: {chatgpt['web_search_citations_count']}")
                print(f"  Response preview: {chatgpt.get('response', '')[:100]}...")
                print()
                count += 1


if __name__ == "__main__":
    print("=" * 60)
    print("Web Search Field Migration Script")
    print("=" * 60)

    # Run migration
    migrate_results()

    # Verify results
    verify_migration()

    print("\n[OK] Migration complete! Your existing data now includes web_search_used fields.")
    print("Going forward, new ChatGPT responses will capture this info directly from the API.")
