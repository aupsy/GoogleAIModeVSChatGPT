"""
Statistical Analysis Module
Performs comprehensive statistical analysis comparing ChatGPT vs Google AI Mode
including t-tests, effect sizes, and categorical breakdowns.
"""

import json
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from collections import defaultdict

import data_manager


def load_analysis_data() -> pd.DataFrame:
    """
    Load all completed queries with scores into a pandas DataFrame.

    Returns:
        DataFrame with columns: query_id, query, category, quality, intent_clarity,
                               chatgpt_*, google_*, scores_*
    """
    queries = data_manager.load_queries()
    results = data_manager.load_results()

    data = []

    for query in queries:
        query_id = str(query['id'])

        if query_id not in results:
            continue

        result = results[query_id]

        # Skip if not fully scored
        if not result.get('scores'):
            continue

        scores = result['scores']

        # Build row
        row = {
            'query_id': query['id'],
            'query': query['query'],
            'category': query['category'],
            'quality': query['quality'],
            'intent_clarity': query['intent_clarity'],

            # ChatGPT scores
            'chatgpt_relevance': scores.get('chatgpt_relevance'),
            'chatgpt_completeness': scores.get('chatgpt_completeness'),
            'chatgpt_source_quality': scores.get('chatgpt_source_quality'),
            'chatgpt_intent_understood': scores.get('chatgpt_intent_understood', False),
            'chatgpt_followups': scores.get('chatgpt_followups', 0),

            # Google AI scores
            'google_relevance': scores.get('google_relevance'),
            'google_completeness': scores.get('google_completeness'),
            'google_source_quality': scores.get('google_source_quality'),
            'google_intent_understood': scores.get('google_intent_understood', False),
            'google_followups': scores.get('google_followups', 0),

            # Response times (if available)
            'chatgpt_response_time': result.get('chatgpt', {}).get('response_time_ms', None),
            'google_response_time': result.get('google', {}).get('response_time_ms', None),

            # Web search usage (ChatGPT only)
            'chatgpt_web_search_used': result.get('chatgpt', {}).get('web_search_used', False),
            'chatgpt_web_search_citations': result.get('chatgpt', {}).get('web_search_citations_count', 0),
        }

        data.append(row)

    return pd.DataFrame(data)


def calculate_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate overall summary statistics.

    Args:
        df: DataFrame with query results

    Returns:
        Dictionary with summary statistics
    """
    if len(df) == 0:
        return {'error': 'No data available'}

    metrics = ['relevance', 'completeness', 'source_quality']

    summary = {
        'total_queries': len(df),
        'chatgpt': {},
        'google': {}
    }

    for platform in ['chatgpt', 'google']:
        stats_dict = {}

        for metric in metrics:
            col = f'{platform}_{metric}'
            if col in df.columns:
                values = df[col].dropna()
                stats_dict[metric] = {
                    'mean': round(values.mean(), 2),
                    'median': round(values.median(), 2),
                    'std': round(values.std(), 2),
                    'min': round(values.min(), 2),
                    'max': round(values.max(), 2)
                }

        # Intent understanding rate
        intent_col = f'{platform}_intent_understood'
        if intent_col in df.columns:
            stats_dict['intent_understanding_rate'] = round(
                df[intent_col].sum() / len(df) * 100, 1
            )

        # Average follow-ups
        followup_col = f'{platform}_followups'
        if followup_col in df.columns:
            stats_dict['avg_followups'] = round(df[followup_col].mean(), 2)

        summary[platform] = stats_dict

    return summary


def paired_t_test(df: pd.DataFrame, metric: str) -> Dict:
    """
    Perform paired t-test comparing ChatGPT vs Google AI for a metric.

    Args:
        df: DataFrame with results
        metric: Metric name ('relevance', 'completeness', 'source_quality')

    Returns:
        Dictionary with test results
    """
    chatgpt_col = f'chatgpt_{metric}'
    google_col = f'google_{metric}'

    if chatgpt_col not in df.columns or google_col not in df.columns:
        return {'error': f'Metric {metric} not found'}

    # Get paired data (drop rows with missing values)
    paired_df = df[[chatgpt_col, google_col]].dropna()

    if len(paired_df) < 2:
        return {'error': 'Insufficient data for t-test'}

    chatgpt_scores = paired_df[chatgpt_col]
    google_scores = paired_df[google_col]

    # Perform paired t-test
    t_statistic, p_value = stats.ttest_rel(chatgpt_scores, google_scores)

    # Calculate means
    chatgpt_mean = chatgpt_scores.mean()
    google_mean = google_scores.mean()

    # Calculate effect size (Cohen's d)
    diff = chatgpt_scores - google_scores
    cohens_d = diff.mean() / diff.std()

    # Determine significance
    significant = p_value < 0.05

    return {
        'metric': metric,
        'n': len(paired_df),
        'chatgpt_mean': round(chatgpt_mean, 2),
        'google_mean': round(google_mean, 2),
        'difference': round(google_mean - chatgpt_mean, 2),
        't_statistic': round(t_statistic, 3),
        'p_value': round(p_value, 4),
        'significant': significant,
        'cohens_d': round(cohens_d, 3),
        'interpretation': interpret_cohens_d(cohens_d)
    }


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"


def performance_by_category(df: pd.DataFrame) -> Dict:
    """
    Calculate performance breakdown by query category.

    Args:
        df: DataFrame with results

    Returns:
        Dictionary with category-wise statistics
    """
    if 'category' not in df.columns:
        return {'error': 'Category column not found'}

    categories = df['category'].unique()
    metrics = ['relevance', 'completeness', 'source_quality']

    results = {}

    for category in categories:
        category_df = df[df['category'] == category]

        category_stats = {
            'count': len(category_df),
            'chatgpt': {},
            'google': {}
        }

        for platform in ['chatgpt', 'google']:
            platform_stats = {}

            for metric in metrics:
                col = f'{platform}_{metric}'
                if col in category_df.columns:
                    values = category_df[col].dropna()
                    if len(values) > 0:
                        platform_stats[metric] = round(values.mean(), 2)

            category_stats[platform] = platform_stats

        results[category] = category_stats

    return results


def performance_by_quality(df: pd.DataFrame) -> Dict:
    """
    Calculate performance breakdown by query quality.

    Args:
        df: DataFrame with results

    Returns:
        Dictionary with quality-wise statistics
    """
    if 'quality' not in df.columns:
        return {'error': 'Quality column not found'}

    qualities = df['quality'].unique()
    metrics = ['relevance', 'completeness', 'source_quality']

    results = {}

    for quality in qualities:
        quality_df = df[df['quality'] == quality]

        quality_stats = {
            'count': len(quality_df),
            'chatgpt': {},
            'google': {}
        }

        for platform in ['chatgpt', 'google']:
            platform_stats = {}

            for metric in metrics:
                col = f'{platform}_{metric}'
                if col in quality_df.columns:
                    values = quality_df[col].dropna()
                    if len(values) > 0:
                        platform_stats[metric] = round(values.mean(), 2)

            # Intent understanding rate for this quality level
            intent_col = f'{platform}_intent_understood'
            if intent_col in quality_df.columns:
                platform_stats['intent_rate'] = round(
                    quality_df[intent_col].sum() / len(quality_df) * 100, 1
                )

            quality_stats[platform] = platform_stats

        results[quality] = quality_stats

    return results


def performance_by_intent_clarity(df: pd.DataFrame) -> Dict:
    """
    Calculate performance breakdown by intent clarity level.

    Args:
        df: DataFrame with results

    Returns:
        Dictionary with intent_clarity-wise statistics
    """
    if 'intent_clarity' not in df.columns:
        return {'error': 'Intent clarity column not found'}

    clarity_levels = df['intent_clarity'].unique()
    metrics = ['relevance', 'completeness', 'source_quality']

    results = {}

    for clarity in clarity_levels:
        clarity_df = df[df['intent_clarity'] == clarity]

        clarity_stats = {
            'count': len(clarity_df),
            'chatgpt': {},
            'google': {}
        }

        for platform in ['chatgpt', 'google']:
            platform_stats = {}

            for metric in metrics:
                col = f'{platform}_{metric}'
                if col in clarity_df.columns:
                    values = clarity_df[col].dropna()
                    if len(values) > 0:
                        platform_stats[metric] = round(values.mean(), 2)

            # Intent understanding rate for this clarity level
            intent_col = f'{platform}_intent_understood'
            if intent_col in clarity_df.columns:
                platform_stats['intent_rate'] = round(
                    clarity_df[intent_col].sum() / len(clarity_df) * 100, 1
                )

            clarity_stats[platform] = platform_stats

        results[clarity] = clarity_stats

    return results


def performance_by_web_search(df: pd.DataFrame) -> Dict:
    """
    Compare ChatGPT performance when web search is used vs not used.

    Args:
        df: DataFrame with results

    Returns:
        Dictionary with web search impact statistics
    """
    if 'chatgpt_web_search_used' not in df.columns:
        return {'error': 'Web search usage data not available'}

    metrics = ['relevance', 'completeness', 'source_quality']

    # Split data by web search usage
    with_search = df[df['chatgpt_web_search_used'] == True]
    without_search = df[df['chatgpt_web_search_used'] == False]

    results = {
        'with_web_search': {
            'count': len(with_search),
            'chatgpt': {}
        },
        'without_web_search': {
            'count': len(without_search),
            'chatgpt': {}
        },
        'comparison': {}
    }

    # Calculate stats for each group
    for metric in metrics:
        col = f'chatgpt_{metric}'

        # With web search
        if len(with_search) > 0 and col in with_search.columns:
            values = with_search[col].dropna()
            if len(values) > 0:
                results['with_web_search']['chatgpt'][metric] = round(values.mean(), 2)

        # Without web search
        if len(without_search) > 0 and col in without_search.columns:
            values = without_search[col].dropna()
            if len(values) > 0:
                results['without_web_search']['chatgpt'][metric] = round(values.mean(), 2)

        # Calculate difference
        if (metric in results['with_web_search']['chatgpt'] and
            metric in results['without_web_search']['chatgpt']):
            diff = (results['with_web_search']['chatgpt'][metric] -
                   results['without_web_search']['chatgpt'][metric])
            results['comparison'][metric] = {
                'difference': round(diff, 2),
                'percent_change': round((diff / results['without_web_search']['chatgpt'][metric]) * 100, 1)
            }

    # Intent understanding comparison
    if len(with_search) > 0:
        intent_rate_with = round(
            with_search['chatgpt_intent_understood'].sum() / len(with_search) * 100, 1
        )
        results['with_web_search']['chatgpt']['intent_rate'] = intent_rate_with

    if len(without_search) > 0:
        intent_rate_without = round(
            without_search['chatgpt_intent_understood'].sum() / len(without_search) * 100, 1
        )
        results['without_web_search']['chatgpt']['intent_rate'] = intent_rate_without

    # Compare vs Google when web search is used
    if len(with_search) > 0:
        results['with_web_search']['google'] = {}
        for metric in metrics:
            google_col = f'google_{metric}'
            if google_col in with_search.columns:
                values = with_search[google_col].dropna()
                if len(values) > 0:
                    results['with_web_search']['google'][metric] = round(values.mean(), 2)

    return results


def generate_full_analysis() -> Dict:
    """
    Generate complete statistical analysis.

    Returns:
        Dictionary with all analysis results
    """
    df = load_analysis_data()

    if len(df) == 0:
        return {'error': 'No scored queries available'}

    analysis = {
        'metadata': {
            'total_queries': len(df),
            'generated_at': pd.Timestamp.now().isoformat()
        },
        'summary_stats': calculate_summary_stats(df),
        'statistical_tests': {},
        'by_category': performance_by_category(df),
        'by_quality': performance_by_quality(df),
        'by_intent_clarity': performance_by_intent_clarity(df),
        'by_web_search': performance_by_web_search(df)
    }

    # Run t-tests for each metric
    for metric in ['relevance', 'completeness', 'source_quality']:
        analysis['statistical_tests'][metric] = paired_t_test(df, metric)

    return analysis


def generate_insights(analysis: Dict) -> List[str]:
    """
    Generate automated insights from the analysis.

    Args:
        analysis: Analysis dictionary from generate_full_analysis()

    Returns:
        List of insight strings
    """
    insights = []

    if 'error' in analysis:
        return [analysis['error']]

    # Overall winner
    summary = analysis.get('summary_stats', {})
    if 'chatgpt' in summary and 'google' in summary:
        chatgpt_avg = np.mean([
            summary['chatgpt'].get('relevance', {}).get('mean', 0),
            summary['chatgpt'].get('completeness', {}).get('mean', 0),
            summary['chatgpt'].get('source_quality', {}).get('mean', 0)
        ])
        google_avg = np.mean([
            summary['google'].get('relevance', {}).get('mean', 0),
            summary['google'].get('completeness', {}).get('mean', 0),
            summary['google'].get('source_quality', {}).get('mean', 0)
        ])

        winner = "Google AI Mode" if google_avg > chatgpt_avg else "ChatGPT"
        diff = abs(google_avg - chatgpt_avg)
        insights.append(f"{winner} has higher overall average scores (+{diff:.2f} points)")

    # Statistical significance
    tests = analysis.get('statistical_tests', {})
    for metric, test_result in tests.items():
        if test_result.get('significant'):
            winner = "Google AI" if test_result['difference'] > 0 else "ChatGPT"
            insights.append(
                f"{winner} significantly outperforms on {metric} "
                f"(p={test_result['p_value']:.4f}, effect size: {test_result['interpretation']})"
            )

    # Intent understanding
    if 'chatgpt' in summary and 'google' in summary:
        chatgpt_intent = summary['chatgpt'].get('intent_understanding_rate', 0)
        google_intent = summary['google'].get('intent_understanding_rate', 0)

        if abs(google_intent - chatgpt_intent) > 5:
            winner = "Google AI Mode" if google_intent > chatgpt_intent else "ChatGPT"
            insights.append(
                f"{winner} better understands user intent "
                f"({max(google_intent, chatgpt_intent):.1f}% vs {min(google_intent, chatgpt_intent):.1f}%)"
            )

    # Quality performance
    quality_results = analysis.get('by_quality', {})
    if 'Poorly-formed' in quality_results:
        poorly_formed = quality_results['Poorly-formed']
        if 'chatgpt' in poorly_formed and 'google' in poorly_formed:
            chatgpt_poorly = np.mean([v for v in poorly_formed['chatgpt'].values() if isinstance(v, (int, float))])
            google_poorly = np.mean([v for v in poorly_formed['google'].values() if isinstance(v, (int, float))])

            if abs(google_poorly - chatgpt_poorly) > 0.3:
                winner = "Google AI Mode" if google_poorly > chatgpt_poorly else "ChatGPT"
                insights.append(
                    f"{winner} handles poorly-formed queries better "
                    f"(testing the intent understanding hypothesis)"
                )

    return insights


if __name__ == "__main__":
    print("Running statistical analysis...\n")

    analysis = generate_full_analysis()

    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
    else:
        print("Analysis Summary:")
        print(f"Total queries analyzed: {analysis['metadata']['total_queries']}")

        print("\nKey Insights:")
        insights = generate_insights(analysis)
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")

        # Print summary stats
        print("\nSummary Statistics:")
        summary = analysis['summary_stats']
        for platform in ['chatgpt', 'google']:
            print(f"\n{platform.upper()}:")
            for metric, values in summary[platform].items():
                if isinstance(values, dict):
                    print(f"  {metric}: {values.get('mean')} (±{values.get('std')})")
                else:
                    print(f"  {metric}: {values}")
