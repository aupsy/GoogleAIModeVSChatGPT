"""
Validation Script - Compare Manual Scores vs LLM Judge
Runs LLM judge on manually scored queries to validate alignment.
"""

import json
from llm_judge import LLMJudge
import data_manager


def validate_llm_judge():
    """Run LLM judge on manually scored queries and compare results."""

    print("="*60)
    print("LLM Judge Validation")
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
        with open('results.json', 'r') as f:
            results_data = json.load(f)
        print(f"[OK] Loaded results.json")
    except Exception as e:
        print(f"[FAIL] Could not load results.json: {e}")
        return

    # Load query dataset for metadata
    try:
        with open('query_dataset.json', 'r') as f:
            query_dataset = json.load(f)
        print(f"[OK] Loaded query_dataset.json")
    except Exception as e:
        print(f"[FAIL] Could not load query_dataset.json: {e}")
        return

    # Get manually scored queries (those with 'scores' field)
    manually_scored = []
    for query_id, data in results_data.items():
        if data.get('scores'):
            # Merge with query dataset for full info
            query_info = query_dataset[int(query_id)]
            manually_scored.append({
                'id': int(query_id),
                'query': query_info['query'],
                'category': query_info['category'],
                'quality': query_info['quality'],
                'intent_clarity': query_info['intent_clarity'],
                'chatgpt_response': data['chatgpt']['response'],
                'google_response': data['google']['response'],
                'manual_scores': data['scores']
            })

    if not manually_scored:
        print("[FAIL] No manually scored queries found")
        return

    print(f"[OK] Found {len(manually_scored)} manually scored queries")
    print()

    # Run LLM judge on each manually scored query
    print("Running LLM judge evaluation...")
    print("-" * 60)

    results = []
    chatgpt_scores_manual = {'relevance': [], 'completeness': [], 'source_quality': [], 'intent': [], 'followups': []}
    chatgpt_scores_llm = {'relevance': [], 'completeness': [], 'source_quality': [], 'intent': [], 'followups': []}
    google_scores_manual = {'relevance': [], 'completeness': [], 'source_quality': [], 'intent': [], 'followups': []}
    google_scores_llm = {'relevance': [], 'completeness': [], 'source_quality': [], 'intent': [], 'followups': []}

    for i, query in enumerate(manually_scored, 1):
        print(f"\n[{i}/{len(manually_scored)}] Query {query['id']}: {query['query'][:50]}...")

        # Get responses
        chatgpt_response = query['chatgpt_response']
        google_response = query['google_response']

        if not chatgpt_response or not google_response:
            print("  [SKIP] Missing responses")
            continue

        # Get manual scores
        manual = query['manual_scores']

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
                chatgpt_response,
                google_response,
                metadata
            )

            if llm_eval and llm_eval['chatgpt'] and llm_eval['google']:
                print("  [OK] LLM evaluation complete")

                # Collect scores for comparison
                # ChatGPT
                chatgpt_scores_manual['relevance'].append(manual.get('chatgpt_relevance', 0))
                chatgpt_scores_manual['completeness'].append(manual.get('chatgpt_completeness', 0))
                chatgpt_scores_manual['source_quality'].append(manual.get('chatgpt_source_quality', 0))
                chatgpt_scores_manual['intent'].append(1 if manual.get('chatgpt_intent_understood') else 0)
                chatgpt_scores_manual['followups'].append(1 if manual.get('chatgpt_followups_needed') else 0)

                chatgpt_scores_llm['relevance'].append(llm_eval['chatgpt']['relevance'])
                chatgpt_scores_llm['completeness'].append(llm_eval['chatgpt']['completeness'])
                chatgpt_scores_llm['source_quality'].append(llm_eval['chatgpt']['source_quality'])
                chatgpt_scores_llm['intent'].append(1 if llm_eval['chatgpt']['intent_understood'] else 0)
                chatgpt_scores_llm['followups'].append(1 if llm_eval['chatgpt']['followups_needed'] else 0)

                # Google
                google_scores_manual['relevance'].append(manual.get('google_relevance', 0))
                google_scores_manual['completeness'].append(manual.get('google_completeness', 0))
                google_scores_manual['source_quality'].append(manual.get('google_source_quality', 0))
                google_scores_manual['intent'].append(1 if manual.get('google_intent_understood') else 0)
                google_scores_manual['followups'].append(1 if manual.get('google_followups_needed') else 0)

                google_scores_llm['relevance'].append(llm_eval['google']['relevance'])
                google_scores_llm['completeness'].append(llm_eval['google']['completeness'])
                google_scores_llm['source_quality'].append(llm_eval['google']['source_quality'])
                google_scores_llm['intent'].append(1 if llm_eval['google']['intent_understood'] else 0)
                google_scores_llm['followups'].append(1 if llm_eval['google']['followups_needed'] else 0)

                results.append({
                    'query_id': query['id'],
                    'query': query['query'],
                    'manual': manual,
                    'llm': llm_eval
                })
            else:
                print("  [FAIL] LLM evaluation returned None")

        except Exception as e:
            print(f"  [FAIL] Error: {e}")

    # Calculate and display alignment metrics
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    print()

    if not results:
        print("[FAIL] No results to compare")
        return

    print(f"Successfully evaluated {len(results)} queries")
    print()

    # Calculate average differences
    def calc_avg_diff(manual_scores, llm_scores):
        if not manual_scores or not llm_scores:
            return 0
        diffs = [abs(m - l) for m, l in zip(manual_scores, llm_scores)]
        return sum(diffs) / len(diffs)

    def calc_avg(scores):
        if not scores:
            return 0
        return sum(scores) / len(scores)

    def calc_agreement(manual_scores, llm_scores):
        """Calculate percentage of exact matches for binary scores"""
        if not manual_scores or not llm_scores:
            return 0
        matches = sum(1 for m, l in zip(manual_scores, llm_scores) if m == l)
        return (matches / len(manual_scores)) * 100

    print("CHATGPT SCORES COMPARISON:")
    print("-" * 60)
    print(f"{'Metric':<20} {'Manual Avg':<15} {'LLM Avg':<15} {'Avg Diff':<15}")
    print("-" * 60)

    for metric in ['relevance', 'completeness', 'source_quality']:
        manual_avg = calc_avg(chatgpt_scores_manual[metric])
        llm_avg = calc_avg(chatgpt_scores_llm[metric])
        diff = calc_avg_diff(chatgpt_scores_manual[metric], chatgpt_scores_llm[metric])
        print(f"{metric.capitalize():<20} {manual_avg:<15.2f} {llm_avg:<15.2f} {diff:<15.2f}")

    print()
    print(f"{'Metric':<20} {'Agreement %':<15}")
    print("-" * 60)
    intent_agree = calc_agreement(chatgpt_scores_manual['intent'], chatgpt_scores_llm['intent'])
    followups_agree = calc_agreement(chatgpt_scores_manual['followups'], chatgpt_scores_llm['followups'])
    print(f"{'Intent Understood':<20} {intent_agree:<15.1f}%")
    print(f"{'Followups Needed':<20} {followups_agree:<15.1f}%")

    print()
    print("GOOGLE AI SCORES COMPARISON:")
    print("-" * 60)
    print(f"{'Metric':<20} {'Manual Avg':<15} {'LLM Avg':<15} {'Avg Diff':<15}")
    print("-" * 60)

    for metric in ['relevance', 'completeness', 'source_quality']:
        manual_avg = calc_avg(google_scores_manual[metric])
        llm_avg = calc_avg(google_scores_llm[metric])
        diff = calc_avg_diff(google_scores_manual[metric], google_scores_llm[metric])
        print(f"{metric.capitalize():<20} {manual_avg:<15.2f} {llm_avg:<15.2f} {diff:<15.2f}")

    print()
    print(f"{'Metric':<20} {'Agreement %':<15}")
    print("-" * 60)
    intent_agree = calc_agreement(google_scores_manual['intent'], google_scores_llm['intent'])
    followups_agree = calc_agreement(google_scores_manual['followups'], google_scores_llm['followups'])
    print(f"{'Intent Understood':<20} {intent_agree:<15.1f}%")
    print(f"{'Followups Needed':<20} {followups_agree:<15.1f}%")

    print()
    print("="*60)
    print("INTERPRETATION GUIDE:")
    print("="*60)
    print("Average Difference (1-5 scale metrics):")
    print("  < 0.5  : Excellent alignment")
    print("  0.5-1.0: Good alignment")
    print("  1.0-1.5: Moderate alignment")
    print("  > 1.5  : Poor alignment - review needed")
    print()
    print("Agreement % (Yes/No metrics):")
    print("  > 80%  : Excellent alignment")
    print("  60-80% : Good alignment")
    print("  40-60% : Moderate alignment")
    print("  < 40%  : Poor alignment - review needed")
    print()

    # Overall recommendation
    print("="*60)
    print("RECOMMENDATION:")
    print("="*60)

    chatgpt_avg_diff = (
        calc_avg_diff(chatgpt_scores_manual['relevance'], chatgpt_scores_llm['relevance']) +
        calc_avg_diff(chatgpt_scores_manual['completeness'], chatgpt_scores_llm['completeness']) +
        calc_avg_diff(chatgpt_scores_manual['source_quality'], chatgpt_scores_llm['source_quality'])
    ) / 3

    google_avg_diff = (
        calc_avg_diff(google_scores_manual['relevance'], google_scores_llm['relevance']) +
        calc_avg_diff(google_scores_manual['completeness'], google_scores_llm['completeness']) +
        calc_avg_diff(google_scores_manual['source_quality'], google_scores_llm['source_quality'])
    ) / 3

    overall_diff = (chatgpt_avg_diff + google_avg_diff) / 2

    print(f"Overall Average Difference: {overall_diff:.2f}")
    print()

    if overall_diff < 0.5:
        print("✓ EXCELLENT alignment! LLM judge is highly reliable.")
        print("  -> Proceed with confidence to score remaining queries")
    elif overall_diff < 1.0:
        print("✓ GOOD alignment! LLM judge is reasonably reliable.")
        print("  -> Safe to proceed with automated scoring")
    elif overall_diff < 1.5:
        print("⚠ MODERATE alignment. Some discrepancies present.")
        print("  -> Review specific cases before proceeding")
        print("  -> Consider adjusting evaluation criteria")
    else:
        print("✗ POOR alignment. Significant discrepancies.")
        print("  -> DO NOT proceed with automated scoring yet")
        print("  -> Review LLM judge prompt and criteria")
        print("  -> Consider manual scoring more queries")

    print()
    print("="*60)
    print("Validation complete!")
    print("="*60)

    # Save detailed results
    with open('validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to: validation_results.json")


if __name__ == "__main__":
    validate_llm_judge()
