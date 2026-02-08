"""
Generate comparison chart for blog post
Shows ChatGPT vs Google AI Mode across all evaluation metrics
"""

import matplotlib.pyplot as plt
import numpy as np
import json

# Load results
with open('results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter scored queries
scored = {k: v for k, v in data.items() if 'scores' in v and v['scores'] is not None and 'chatgpt_relevance' in v['scores']}
print(f'Analyzing {len(scored)} scored queries...')

# Calculate averages
chatgpt_rel = [v['scores']['chatgpt_relevance'] for v in scored.values()]
chatgpt_comp = [v['scores']['chatgpt_completeness'] for v in scored.values()]
chatgpt_src = [v['scores']['chatgpt_source_quality'] for v in scored.values()]
chatgpt_intent = [1 if v['scores']['chatgpt_intent_understood'] else 0 for v in scored.values()]

google_rel = [v['scores']['google_relevance'] for v in scored.values()]
google_comp = [v['scores']['google_completeness'] for v in scored.values()]
google_src = [v['scores']['google_source_quality'] for v in scored.values()]
google_intent = [1 if v['scores']['google_intent_understood'] else 0 for v in scored.values()]

# Calculate means
chatgpt_means = [
    np.mean(chatgpt_rel),
    np.mean(chatgpt_comp),
    np.mean(chatgpt_src),
    np.mean(chatgpt_intent) * 5  # Scale to 5 for visualization
]

google_means = [
    np.mean(google_rel),
    np.mean(google_comp),
    np.mean(google_src),
    np.mean(google_intent) * 5  # Scale to 5 for visualization
]

# Chart 1: Grouped Bar Chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

metrics = ['Relevance', 'Completeness', 'Source\nQuality', 'Intent\nUnderstanding']
x = np.arange(len(metrics))
width = 0.35

bars1 = ax1.bar(x - width/2, chatgpt_means, width, label='ChatGPT', color='#10A37F', alpha=0.8)
bars2 = ax1.bar(x + width/2, google_means, width, label='Google AI Mode', color='#4285F4', alpha=0.8)

ax1.set_ylabel('Score (out of 5)', fontsize=12, fontweight='bold')
ax1.set_title('ChatGPT vs Google AI Mode Performance\n(192 Queries Evaluated)', fontsize=14, fontweight='bold', pad=20)
ax1.set_xticks(x)
ax1.set_xticklabels(metrics, fontsize=11)
ax1.legend(fontsize=11, loc='upper left')
ax1.set_ylim(0, 5.5)
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.axhline(y=5.0, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

# Chart 2: Difference Chart (Google - ChatGPT)
differences = [google_means[i] - chatgpt_means[i] for i in range(len(metrics))]
colors = ['#4285F4' if d > 0 else '#10A37F' for d in differences]

bars3 = ax2.barh(metrics, differences, color=colors, alpha=0.8)

ax2.set_xlabel('Score Difference (Google - ChatGPT)', fontsize=12, fontweight='bold')
ax2.set_title('Performance Gap Analysis\n(Positive = Google Advantage)', fontsize=14, fontweight='bold', pad=20)
ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax2.grid(axis='x', alpha=0.3, linestyle='--')

# Add value labels
for i, (bar, diff) in enumerate(zip(bars3, differences)):
    label = f'{diff:+.2f}'
    x_pos = diff + (0.05 if diff > 0 else -0.05)
    ha = 'left' if diff > 0 else 'right'
    ax2.text(x_pos, i, label, va='center', ha=ha, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('comparison_chart.png', dpi=300, bbox_inches='tight', facecolor='white')
print('[OK] Saved comparison_chart.png')

# Chart 3: Detailed Metrics with Actual Percentages
fig, ax = plt.subplots(figsize=(10, 6))

# Recalculate with actual percentages for intent understanding
chatgpt_display = [
    np.mean(chatgpt_rel),
    np.mean(chatgpt_comp),
    np.mean(chatgpt_src),
    np.mean(chatgpt_intent) * 100  # Keep as percentage
]

google_display = [
    np.mean(google_rel),
    np.mean(google_comp),
    np.mean(google_src),
    np.mean(google_intent) * 100  # Keep as percentage
]

metrics_detailed = ['Relevance\n(1-5)', 'Completeness\n(1-5)', 'Source Quality\n(1-5)', 'Intent Understanding\n(%)']
x = np.arange(len(metrics_detailed))
width = 0.35

bars1 = ax.bar(x - width/2, [chatgpt_display[0], chatgpt_display[1], chatgpt_display[2], chatgpt_display[3]/20],
               width, label='ChatGPT', color='#10A37F', alpha=0.8)
bars2 = ax.bar(x + width/2, [google_display[0], google_display[1], google_display[2], google_display[3]/20],
               width, label='Google AI Mode', color='#4285F4', alpha=0.8)

ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title('AI Platform Comparison: ChatGPT vs Google AI Mode\n192 Queries Across 6 Categories',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(metrics_detailed, fontsize=10)
ax.legend(fontsize=11, loc='upper right')
ax.set_ylim(0, 5.5)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels with proper formatting
for i, bar in enumerate(bars1):
    height = bar.get_height()
    if i < 3:
        label = f'{chatgpt_display[i]:.2f}'
    else:
        label = f'{chatgpt_display[i]:.1f}%'
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            label, ha='center', va='bottom', fontsize=9, fontweight='bold')

for i, bar in enumerate(bars2):
    height = bar.get_height()
    if i < 3:
        label = f'{google_display[i]:.2f}'
    else:
        label = f'{google_display[i]:.1f}%'
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            label, ha='center', va='bottom', fontsize=9, fontweight='bold')

# Add note about intent understanding scaling
ax.text(0.5, -0.15, 'Note: Intent Understanding shown as percentage divided by 20 for scale consistency',
        transform=ax.transAxes, ha='center', fontsize=9, style='italic', color='gray')

plt.tight_layout()
plt.savefig('detailed_comparison_chart.png', dpi=300, bbox_inches='tight', facecolor='white')
print('[OK] Saved detailed_comparison_chart.png')

# Print summary statistics
print('\n=== SUMMARY STATISTICS ===')
print(f'ChatGPT Scores:')
print(f'  Relevance: {np.mean(chatgpt_rel):.2f}/5')
print(f'  Completeness: {np.mean(chatgpt_comp):.2f}/5')
print(f'  Source Quality: {np.mean(chatgpt_src):.2f}/5')
print(f'  Intent Understanding: {np.mean(chatgpt_intent)*100:.1f}%')
print()
print(f'Google AI Mode Scores:')
print(f'  Relevance: {np.mean(google_rel):.2f}/5')
print(f'  Completeness: {np.mean(google_comp):.2f}/5')
print(f'  Source Quality: {np.mean(google_src):.2f}/5')
print(f'  Intent Understanding: {np.mean(google_intent)*100:.1f}%')

print('\n[OK] Charts created successfully!')
print('  - comparison_chart.png (side-by-side comparison)')
print('  - detailed_comparison_chart.png (single detailed view)')
