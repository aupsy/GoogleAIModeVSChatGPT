import json

# Load results
with open('results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

print(f"Total entries in results.json: {len(results)}")
print(f"First 5 keys: {list(results.keys())[:5]}")

chatgpt_done = 0
google_done = 0
scored = 0

for qid_str in results:
    entry = results[qid_str]
    has_chatgpt = bool(entry.get('chatgpt'))
    has_google = bool(entry.get('google'))
    has_scores = bool(entry.get('scores') or entry.get('llm_scores'))

    if has_chatgpt:
        chatgpt_done += 1
    if has_google:
        google_done += 1
    if has_scores:
        scored += 1

print(f"\nChatGPT responses: {chatgpt_done}")
print(f"Google responses: {google_done}")
print(f"Scored: {scored}")

# Now test via data_manager
print("\n--- Testing via data_manager ---")
import data_manager
stats = data_manager.get_completion_stats()
print(stats)
