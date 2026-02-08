# AI Assistant Testing Query Dataset
**Total Queries: 200**  
**Created: December 30, 2025**

## Purpose
This dataset is designed to test the hypothesis that Google's AI mode performs better than vanilla LLM assistants (like ChatGPT) due to:
1. Superior underlying model (Gemini 3)
2. Better intent understanding from Google Search infrastructure

## Dataset Structure
The dataset includes 200 queries across 6 categories with varying quality levels to specifically test intent understanding and model capabilities.

### Distribution Summary

**By Category:**
- Informational: 50 queries (25%)
- Transactional: 40 queries (20%)
- Comparative: 40 queries (20%)
- Procedural: 30 queries (15%)
- Real-time/Current: 20 queries (10%)
- Complex Multi-hop: 20 queries (10%)

**By Query Quality:**
- Well-formed: 70 queries (35%)
- Poorly-formed: 86 queries (43%)
- Ambiguous: 35 queries (17.5%)
- Typos/Informal: 5 queries (2.5%)
- Time-sensitive ambiguous: 4 queries (2%)

**By Intent Clarity:**
- High: 70 queries (35%)
- Medium: 5 queries (2.5%)
- Low: 86 queries (43%)
- Very Low: 39 queries (19.5%)

---

## Testing Instructions

### Recommended Testing Protocol

1. **Run each query on both platforms** (Google AI Mode and ChatGPT)
2. **Record the following metrics:**
   - Response time
   - Answer relevance (1-5 scale)
   - Completeness (1-5 scale)
   - Source quality (1-5 scale)
   - Intent interpretation accuracy (Did it understand what you meant?)
   - Follow-up questions needed (count)

3. **Pay special attention to:**
   - How each platform handles poorly-formed queries
   - Whether clarifying questions are asked
   - Quality of default assumptions made
   - Ability to infer missing context

---

## Category: Informational (50 queries)

### Well-formed (15 queries)
*Intent Clarity: High*

1. What are the health benefits of intermittent fasting for adults over 40?
2. Explain the difference between machine learning and deep learning with examples
3. What caused the 2008 financial crisis and what were its long-term effects?
4. How does CRISPR gene editing technology work at the molecular level?
5. What are the main features of the James Webb Space Telescope?
6. What is the current scientific consensus on climate change causes?
7. How do mRNA vaccines work compared to traditional vaccines?
8. What are the key principles of sustainable architecture?
9. Explain the differences between Keynesian and Austrian economics
10. What are the nutritional differences between plant-based and animal proteins?
11. How does quantum computing differ from classical computing?
12. What is the history and cultural significance of the Silk Road?
13. What are the main causes and symptoms of burnout syndrome?
14. How does blockchain technology enable cryptocurrency transactions?
15. What are the psychological effects of social media use on teenagers?

### Poorly-formed (20 queries)
*Intent Clarity: Low*

1. best laptop
2. how to lose weight
3. crypto
4. is coffee good
5. python vs javascript
6. climate change facts
7. what is AI
8. meditation benefits
9. electric cars
10. how to invest
11. quantum physics
12. sleep better
13. keto diet
14. remote work
15. memory improvement
16. stress management
17. blockchain explained
18. yoga for beginners
19. intermittent fasting
20. sustainable living

### Ambiguous (15 queries)
*Intent Clarity: Very Low*

1. What's the best way to learn?
2. How much does it cost?
3. Is this safe?
4. When should I start?
5. Which one is better?
6. Can you explain the process?
7. What are the side effects?
8. How long does it take?
9. Is it worth it?
10. What do experts say?
11. How does it compare?
12. What are the requirements?
13. Is there a better alternative?
14. What's the latest research?
15. How do I know if it's working?

---

## Category: Transactional (40 queries)

### Well-formed (10 queries)
*Intent Clarity: High*

1. Best noise-canceling headphones under $300 for frequent travelers in 2025
2. Where can I buy organic skincare products with free shipping to Canada?
3. Compare prices for iPhone 16 Pro across major retailers
4. Best budget gaming laptop with RTX 4060 GPU under $1200
5. Top-rated standing desks for home office under $500
6. Where to buy sustainable running shoes in Vancouver?
7. Best air purifier for allergies under $200 with HEPA filter
8. Compare Tesla Model 3 vs BMW i4 pricing and features
9. Affordable ergonomic office chairs with lumbar support under $400
10. Best meal kit delivery services in British Columbia for vegetarians

### Poorly-formed (20 queries)
*Intent Clarity: Low*

1. cheap headphones
2. where to buy laptop
3. best phone 2025
4. affordable furniture
5. gaming setup
6. running shoes deals
7. buy vitamins
8. cheap flights
9. hotel deals
10. camera for photography
11. monitor for gaming
12. coffee maker
13. vacuum cleaner
14. mattress recommendations
15. winter jacket
16. smart watch
17. blender price
18. electric toothbrush
19. luggage set
20. kitchen knife

### Ambiguous (10 queries)
*Intent Clarity: Very Low*

1. Where can I get the best deal?
2. Is there a discount available?
3. What's a good brand?
4. Should I buy now or wait?
5. Which model is recommended?
6. Where do people usually buy this?
7. Is this the right price?
8. What are others buying?
9. Is there something better?
10. Where's the cheapest place?

---

## Category: Comparative (40 queries)

### Well-formed (15 queries)
*Intent Clarity: High*

1. Compare Google Gemini vs ChatGPT-4 for code generation tasks
2. What are the pros and cons of solar panels vs wind turbines for home energy?
3. iPhone 16 vs Samsung Galaxy S25: which has better camera performance?
4. Compare tax implications of RRSP vs TFSA for retirement savings in Canada
5. React vs Vue.js: which is better for building enterprise web applications?
6. Compare effectiveness of cognitive behavioral therapy vs medication for anxiety
7. MacBook Air M3 vs Dell XPS 13: which offers better value for students?
8. Renting vs buying a home in Vancouver: financial analysis for 2025
9. Compare nutritional benefits of Mediterranean diet vs paleo diet
10. AWS vs Azure vs Google Cloud: which is best for startups?
11. Electric vehicle vs hybrid vs gas car: total cost of ownership analysis
12. Compare Spotify vs Apple Music vs YouTube Music features and pricing
13. Remote work vs office work: productivity and wellbeing comparison
14. Index funds vs ETFs vs mutual funds: which is best for beginners?
15. Compare French press vs pour-over vs espresso machine coffee quality

### Poorly-formed (15 queries)
*Intent Clarity: Low*

1. iOS vs Android
2. Mac vs PC
3. Netflix vs Disney+
4. gas vs electric
5. freelance vs full-time
6. morning vs evening workout
7. tea vs coffee
8. cardio vs weights
9. city vs suburbs
10. online vs in-person learning
11. cats vs dogs
12. summer vs winter vacation
13. book vs audiobook
14. organic vs regular food
15. startup vs corporate job

### Ambiguous (10 queries)
*Intent Clarity: Very Low*

1. Which one should I choose?
2. What's the difference between them?
3. Which is more popular?
4. What do most people prefer?
5. Is one better than the other?
6. Which has better reviews?
7. What are the main differences?
8. Which is more reliable?
9. What would you recommend?
10. Which gives better results?

---

## Category: Procedural (30 queries)

### Well-formed (10 queries)
*Intent Clarity: High*

1. Step-by-step guide to set up a home network with WiFi 6 router
2. How to create a professional LinkedIn profile that attracts recruiters
3. Complete guide to filing taxes in Canada as a freelancer for 2025
4. How to train for a half marathon in 12 weeks for beginners
5. Step-by-step process to start an LLC in British Columbia
6. How to build a diversified investment portfolio with $10,000
7. Guide to troubleshooting common WiFi connectivity issues at home
8. How to create engaging Instagram Reels for business marketing
9. Complete process for applying to Canadian universities as an international student
10. How to negotiate a job offer salary and benefits effectively

### Poorly-formed (15 queries)
*Intent Clarity: Low*

1. how to code
2. learn Spanish fast
3. start a business
4. make money online
5. build muscle
6. improve credit score
7. grow Instagram followers
8. bake bread
9. meditate properly
10. write a resume
11. take better photos
12. save money
13. network effectively
14. study efficiently
15. wake up early

### Typos/Informal (5 queries)
*Intent Clarity: Medium*

1. how do i fix my computr screen
2. whats the best way too learn guitar
3. how can i loose weight quikly
4. were can i find good recepies
5. how to make my phone baterry last longer

---

## Category: Real-time/Current (20 queries)

### Well-formed (8 queries)
*Intent Clarity: High*

1. What are the latest developments in the 2025 US presidential election?
2. Current stock price and performance of NVIDIA in December 2025
3. Latest news on artificial intelligence regulation in the European Union
4. What is the current inflation rate in Canada as of December 2025?
5. Recent updates on SpaceX Starship development and launch schedule
6. Latest COVID-19 variants and vaccine recommendations for winter 2025
7. Current status of the war in Ukraine as of December 2025
8. Recent breakthrough in quantum computing announced in 2025

### Poorly-formed (8 queries)
*Intent Clarity: Low*

1. latest news
2. stock market today
3. weather this week
4. sports scores
5. what's trending
6. new movies
7. tech news
8. crypto prices

### Time-sensitive ambiguous (4 queries)
*Intent Clarity: Very Low*

1. Is it going to rain tomorrow?
2. What happened yesterday?
3. When is the next holiday?
4. What's the score?

---

## Category: Complex Multi-hop (20 queries)

### Well-formed (12 queries)
*Intent Clarity: High*

1. If I invest $50,000 in an index fund with 7% average annual return, how much will I have in 30 years accounting for inflation?
2. What are the environmental, economic, and social impacts of transitioning to renewable energy in developing countries?
3. Compare the career trajectories, salary potential, and job satisfaction of software engineers vs data scientists in 2025
4. What would be the health, financial, and lifestyle implications of moving from Toronto to Vancouver?
5. Analyze the relationship between interest rates, housing prices, and consumer spending in Canada
6. What are the interconnected causes of the global semiconductor shortage and its impact on various industries?
7. How do different parenting styles affect child development across cognitive, emotional, and social domains?
8. What are the cascading effects of remote work on urban planning, commercial real estate, and public transportation?
9. Compare the long-term effects of different dietary approaches on metabolic health, longevity, and disease prevention
10. What are the geopolitical, economic, and technological factors driving AI development globally?
11. Analyze the relationship between education level, income inequality, and social mobility in developed countries
12. What are the interconnected challenges and solutions for sustainable urban development in megacities?

### Poorly-formed (8 queries)
*Intent Clarity: Low*

1. best career path
2. how to be successful
3. is college worth it
4. should I change jobs
5. best place to live
6. how to be happy
7. what should I invest in
8. best way to retire early

---

## Appendix: Testing Matrix Template

Use this template to record results for each query:

| Query ID | Query Text | Platform | Response Time | Relevance (1-5) | Completeness (1-5) | Source Quality (1-5) | Intent Understood? | Follow-ups Needed | Notes |
|----------|-----------|----------|---------------|-----------------|-------------------|---------------------|-------------------|------------------|-------|
| 1 | [query] | Google AI | | | | | Y/N | | |
| 1 | [query] | ChatGPT | | | | | Y/N | | |

### Scoring Rubrics

**Relevance (1-5):**
- 1: Completely off-topic
- 2: Somewhat related but misses the point
- 3: Addresses the query but lacks focus
- 4: Highly relevant with minor gaps
- 5: Perfectly addresses the query intent

**Completeness (1-5):**
- 1: Severely incomplete, missing critical information
- 2: Partial answer with significant gaps
- 3: Covers basics but lacks depth
- 4: Comprehensive with minor omissions
- 5: Thorough and complete answer

**Source Quality (1-5):**
- 1: No sources or unreliable sources
- 2: Questionable source credibility
- 3: Mix of reliable and less reliable sources
- 4: Mostly authoritative sources
- 5: All high-quality, authoritative sources

**Intent Understanding:**
- Did the system correctly interpret what the user was really asking?
- For poorly-formed queries: Did it make reasonable inferences?
- Did it ask clarifying questions when appropriate?

---

## Analysis Recommendations

After collecting data, analyze:

1. **Performance by Query Quality:**
   - Compare success rates on well-formed vs poorly-formed queries
   - This directly tests the intent understanding hypothesis

2. **Performance by Category:**
   - Identify which types of queries each system handles better
   - Look for patterns in strengths and weaknesses

3. **Intent Clarity Correlation:**
   - Plot performance against intent clarity levels
   - Expected: Google AI Mode should show smaller performance drop-off for low clarity queries

4. **Statistical Significance:**
   - Use paired t-tests to compare mean scores
   - Calculate effect sizes (Cohen's d)
   - Report confidence intervals

5. **Qualitative Patterns:**
   - Document specific examples where intent understanding made a difference
   - Identify systematic errors or strengths

---

## JSON Export

A machine-readable version of this dataset is available in `query_dataset.json` for automated testing scripts.

Each entry contains:
```json
{
  "query": "The actual query text",
  "category": "Category name",
  "quality": "Quality level",
  "intent_clarity": "Clarity level"
}
```

---

*Dataset created for testing Google AI Mode vs ChatGPT performance and intent understanding capabilities.*
