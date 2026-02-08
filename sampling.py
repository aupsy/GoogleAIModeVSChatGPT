"""
Sampling Module
Selects a representative sample of queries for manual scoring validation.
"""

import random
from typing import List, Dict


def select_stratified_sample(queries: List[Dict], sample_size: int = 20) -> List[Dict]:
    """
    Select a stratified sample of queries covering diverse characteristics.

    Ensures the sample includes:
    - Different categories
    - Different quality levels
    - Different intent clarity levels

    Args:
        queries: List of query dictionaries with metadata
        sample_size: Number of queries to sample (default 20)

    Returns:
        List of sampled query dictionaries
    """
    # Group queries by characteristics
    by_category = {}
    by_quality = {}
    by_intent = {}

    for query in queries:
        # Group by category
        category = query.get('category', 'Unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(query)

        # Group by quality
        quality = query.get('quality', 'Unknown')
        if quality not in by_quality:
            by_quality[quality] = []
        by_quality[quality].append(query)

        # Group by intent clarity
        intent = query.get('intent_clarity', 'Unknown')
        if intent not in by_intent:
            by_intent[intent] = []
        by_intent[intent].append(query)

    # Calculate distribution for stratified sampling
    categories = list(by_category.keys())
    qualities = list(by_quality.keys())
    intents = list(by_intent.keys())

    # Proportional allocation
    samples_per_category = max(1, sample_size // len(categories))
    samples_per_quality = max(1, sample_size // len(qualities))
    samples_per_intent = max(1, sample_size // len(intents))

    selected = []
    selected_ids = set()

    # Sample by category first (ensures diversity)
    for category in categories:
        available = [q for q in by_category[category] if q['id'] not in selected_ids]
        n = min(samples_per_category, len(available))
        sampled = random.sample(available, n)
        selected.extend(sampled)
        selected_ids.update(q['id'] for q in sampled)

    # Fill remaining slots with quality/intent diversity
    remaining = sample_size - len(selected)

    if remaining > 0:
        # Prioritize poor quality and low intent (these are harder cases)
        priority_groups = []

        # Poor quality queries
        poor_quality = by_quality.get('Poorly-formed', []) + by_quality.get('Ambiguous', [])
        priority_groups.extend([q for q in poor_quality if q['id'] not in selected_ids])

        # Low intent queries
        low_intent = by_intent.get('Low', []) + by_intent.get('Very Low', [])
        priority_groups.extend([q for q in low_intent if q['id'] not in selected_ids])

        # Remove duplicates
        priority_groups = list({q['id']: q for q in priority_groups}.values())

        if priority_groups:
            n = min(remaining, len(priority_groups))
            sampled = random.sample(priority_groups, n)
            selected.extend(sampled)
            selected_ids.update(q['id'] for q in sampled)
            remaining -= n

    # Fill any remaining with random samples
    if remaining > 0:
        available = [q for q in queries if q['id'] not in selected_ids]
        if available:
            n = min(remaining, len(available))
            sampled = random.sample(available, n)
            selected.extend(sampled)

    # Sort by ID for consistent ordering
    selected.sort(key=lambda q: q['id'])

    return selected


def get_sample_distribution(sample: List[Dict]) -> Dict:
    """
    Analyze the distribution of a sample.

    Returns statistics about the sample composition.
    """
    if not sample:
        return {}

    categories = {}
    qualities = {}
    intents = {}

    for query in sample:
        cat = query.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1

        qual = query.get('quality', 'Unknown')
        qualities[qual] = qualities.get(qual, 0) + 1

        intent = query.get('intent_clarity', 'Unknown')
        intents[intent] = intents.get(intent, 0) + 1

    return {
        'total': len(sample),
        'by_category': categories,
        'by_quality': qualities,
        'by_intent_clarity': intents
    }


if __name__ == "__main__":
    # Test sampling
    import data_manager

    queries = data_manager.load_queries()

    if queries:
        print(f"Total queries: {len(queries)}")

        sample = select_stratified_sample(queries, sample_size=20)
        print(f"\nSelected {len(sample)} queries for manual scoring")

        dist = get_sample_distribution(sample)
        print("\nSample distribution:")
        print(f"  By category: {dist['by_category']}")
        print(f"  By quality: {dist['by_quality']}")
        print(f"  By intent clarity: {dist['by_intent_clarity']}")

        print("\nSample query IDs:", [q['id'] for q in sample])
