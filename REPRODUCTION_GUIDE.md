# Complete Reproduction Guide

This guide provides step-by-step instructions to replicate the "ChatGPT vs Google AI Mode" study from scratch.

**Estimated Time:** 3-4 hours total (varies by number of queries)
**Cost:** ~$1-2 for 200 queries (OpenAI API usage)

---

## Prerequisites

### 1. System Requirements
- **Operating System:** Windows, macOS, or Linux
- **Python:** Version 3.10 or higher (Python 3.14 used in original study)
- **Browser:** Modern web browser (Chrome, Firefox, Edge, Safari)
- **Internet Connection:** Stable connection required

### 2. Required Accounts
- **OpenAI Account:** [Sign up](https://platform.openai.com/signup)
  - API access enabled
  - Payment method configured
  - API key generated
- **Google Account:** Standard Google account
  - Access to Google Search
  - AI Mode enabled (automatic in most regions)

### 3. Technical Skills
- Basic command line usage
- Basic understanding of web browsers
- Ability to copy/paste text
- (Optional) Basic Python knowledge for customization

---

## Part 1: Environment Setup

### Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/aupsy/GoogleAIModeVSChatGPT.git
cd GoogleAIModeVSChatGPT

# OR using SSH
git clone git@github.com:aupsy/GoogleAIModeVSChatGPT.git
cd GoogleAIModeVSChatGPT
```

### Step 2: Verify Python Installation

```bash
# Check Python version
python --version
# Should show: Python 3.10.0 or higher

# If 'python' doesn't work, try 'python3'
python3 --version
```

**Troubleshooting:**
- **Python not found:** [Download Python](https://www.python.org/downloads/)
- **Version too old:** Install Python 3.10+ from official website

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

**Why Virtual Environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Easy to delete and recreate if issues arise

### Step 4: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages:**
- Flask 3.1.2+
- openai 2.14.0+
- pandas 2.3.3+
- scipy 1.16.3+
- matplotlib 3.10.8+
- openpyxl 3.1.5+
- python-dotenv 1.2.1+

**Troubleshooting:**
- **Installation fails:** Try `pip install --upgrade setuptools wheel` first
- **Permission errors:** Use `pip install --user -r requirements.txt`
- **Network issues:** Check internet connection, try again

### Step 5: Configure OpenAI API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your favorite text editor
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env

# Add your OpenAI API key:
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

**Get your API key:**
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Name it: "AI Comparison Study"
4. Copy the key (starts with `sk-proj-...`)
5. Paste into `.env` file

**⚠️ Important:** Never commit `.env` to git! It's already in `.gitignore`.

### Step 6: Configure Application Settings (Optional)

Edit `config.json` to customize:

```json
{
  "model": "gpt-4o-mini-search-preview",  // ChatGPT model to use
  "temperature": 0.7,                      // Response randomness (0-1)
  "batch_size": 10,                        // Default batch size
  "rate_limit_delay": 1.0                  // Seconds between API calls
}
```

**Model Options:**
- `gpt-4o-mini-search-preview`: Current default (with web search)
- `gpt-4-turbo`: Previous generation
- `gpt-4o`: Latest GPT-4 variant

### Step 7: Verify Installation

```bash
# Test the application
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
Press CTRL+C to quit
```

**Open browser:** `http://localhost:5000`

**You should see:** Web interface with buttons for:
- Run ChatGPT Batch
- Enter Google AI Response
- Score Responses
- Export Report

**If it works:** ✅ Setup complete! Press CTRL+C to stop the server.

---

## Part 2: Data Collection

### Phase A: Collect ChatGPT Responses (Automated)

**Time:** ~20 minutes for 200 queries
**Cost:** ~$1-2 total

#### Step 1: Start the Application

```bash
python app.py
```

Open browser: `http://localhost:5000`

#### Step 2: Run First Batch

1. Click **"Run ChatGPT Batch"** button
2. Select batch size:
   - **Start with 10** (recommended for testing)
   - Later increase to 20-50 for efficiency
3. Click **"Start Batch"**
4. Watch the progress bar

**What happens:**
- Application sends queries to OpenAI API
- Responses saved automatically
- Progress tracked in `progress.json`
- Results stored in `results.json`

#### Step 3: Monitor Progress

- Progress bar shows completion percentage
- Status messages update in real-time
- Estimated time remaining displayed

**If you see errors:**
- "Invalid API key" → Check `.env` file
- "Rate limit exceeded" → Wait 60 seconds, try again
- "Network error" → Check internet connection

#### Step 4: Continue Until 200 Queries Complete

**Recommendation:**
- Run batches of 20-50 queries
- Take breaks between batches
- Monitor OpenAI usage dashboard: [OpenAI Usage](https://platform.openai.com/usage)

**Checkpoints:**
- ✅ 50 queries: ~$0.25-0.50 spent
- ✅ 100 queries: ~$0.50-1.00 spent
- ✅ 200 queries: ~$1.00-2.00 spent

#### Step 5: Verify ChatGPT Collection

```bash
# Check how many queries have ChatGPT responses
python -c "import json; data=json.load(open('results.json','r',encoding='utf-8')); print(f'ChatGPT responses: {sum(1 for v in data.values() if \"chatgpt\" in v)}/200')"
```

**Expected:** "ChatGPT responses: 200/200"

---

### Phase B: Collect Google AI Mode Responses (Manual)

**Time:** ~1-1.5 hours for 200 queries
**Cost:** Free

#### Step 1: Prepare Your Workspace

1. **Open the application:** `http://localhost:5000`
2. **Open Google in new tab/window:** `https://google.com`
3. **Verify AI Mode is enabled:**
   - Search for any query
   - Look for "AI Overview" or AI-generated response
   - If not visible, enable in Google Labs: [Google Labs](https://labs.google.com)

**Pro Tip:** Use a second monitor or split-screen for efficiency.

#### Step 2: Start Google Response Entry

1. In application, click **"Enter Google AI Response"**
2. Modal shows:
   - Query text
   - Query metadata (category, quality, intent)
   - Copy button
   - Large text area for response

#### Step 3: Process Each Query

**For each query:**

1. **Click "Copy Query"** button
2. **Switch to Google tab**
3. **Paste query into Google Search**
4. **Wait for AI Mode response** (usually appears at top)
5. **Copy the entire AI response:**
   - Click and drag to select all text
   - Ctrl+C (Windows/Linux) or Cmd+C (macOS)
6. **Switch back to application**
7. **Paste into text area:**
   - Ctrl+V (Windows/Linux) or Cmd+V (macOS)
8. **Click "Save"**
9. **Repeat for next query**

**Keyboard Shortcuts:**
- `Ctrl+Enter`: Save and advance to next query
- `Escape`: Close modal
- `Tab`: Navigate between buttons

#### Step 4: Handle Edge Cases

**No AI response visible:**
- Note: "No AI response generated"
- Save as-is or enter: "[No AI response]"

**Very long response:**
- Copy entire response including all sections
- Preserve formatting when possible

**Response cut off:**
- Click "Show more" or "..." to expand
- Copy full expanded response

#### Step 5: Take Breaks

**Recommended schedule:**
- 20 queries → 5-minute break
- 50 queries → 15-minute break
- Stretch, hydrate, rest eyes

**Application features:**
- Auto-saves every 2 seconds
- Progress tracked automatically
- Can resume anytime

#### Step 6: Verify Google Collection

```bash
# Check how many queries have Google responses
python -c "import json; data=json.load(open('results.json','r',encoding='utf-8')); print(f'Google responses: {sum(1 for v in data.values() if \"google\" in v)}/200')"
```

**Expected:** "Google responses: 200/200"

---

### Phase C: Score Responses (Manual Evaluation)

**Time:** ~1-1.5 hours for 200 queries
**Method:** Manual human evaluation

#### Step 1: Understand Scoring Criteria

Before starting, review the 5 metrics:

**1. Relevance (1-5):**
- 5: Perfectly addresses the question
- 4: Mostly relevant with minor tangents
- 3: Partially relevant
- 2: Loosely related
- 1: Irrelevant

**2. Completeness (1-5):**
- 5: Comprehensive, nothing missing
- 4: Thorough but minor gaps
- 3: Adequate but incomplete
- 2: Missing significant information
- 1: Superficial

**3. Source Quality (1-5):**
- 5: Highly authoritative sources
- 4: Reliable sources
- 3: Mixed quality or unclear sourcing
- 2: Questionable reliability
- 1: Poor or no sources

**4. Intent Understanding (Boolean):**
- ✓ Yes: Clearly understood what user wanted
- ✗ No: Misunderstood or missed the point

**5. Follow-ups Needed (Boolean):**
- ✓ Yes: User would need to search again
- ✗ No: Response is sufficient

#### Step 2: Start Scoring Interface

1. Click **"Score Responses"** button
2. Interface shows:
   - Query at top
   - ChatGPT response (left column, green border)
   - Google response (right column, blue border)
   - Scoring sliders for each metric
   - Checkboxes for boolean metrics
   - Optional notes field

#### Step 3: Score Each Query

**Process:**

1. **Read the query carefully** - Understand what the user is asking
2. **Read ChatGPT response** - Evaluate quality
3. **Read Google response** - Evaluate quality
4. **Compare both responses**
5. **Score ChatGPT** on all 5 metrics
6. **Score Google** on all 5 metrics
7. **(Optional)** Add notes about key differences
8. **Click "Submit"**
9. **Move to next query**

**Tips for Consistency:**
- Take your time (2-3 minutes per query)
- Be fair to both platforms
- Use the full range (don't default to 3-4)
- Consider the query context (well-formed vs poorly-formed)
- Focus on what user needs, not technical perfection

#### Step 4: Handle Difficult Cases

**Both responses are excellent:**
- It's okay to give both high scores
- Differentiate on subtle factors (brevity, clarity, sources)

**Both responses are poor:**
- It's okay to give both low scores
- Note what's missing in notes field

**One response is much better:**
- Reflect this in scores (e.g., 5 vs 2)
- Explain why in notes

**Unsure about intent:**
- Put yourself in user's shoes
- Consider most likely interpretation
- Mark "intent understood" if response addresses likely intent

#### Step 5: Monitor Your Progress

- Progress indicator shows completion percentage
- Status message shows queries remaining
- Auto-save ensures no lost work

#### Step 6: Verify Scoring Complete

```bash
# Check how many queries are scored
python -c "import json; data=json.load(open('results.json','r',encoding='utf-8')); scored=sum(1 for v in data.values() if 'scores' in v and v['scores'] and 'chatgpt_relevance' in v['scores']); print(f'Scored: {scored}/200')"
```

**Expected:** "Scored: 200/200" (or your target number)

---

## Part 3: Analysis and Reporting

### Step 1: Generate Excel Report

1. Click **"Export Report"** button
2. File downloads automatically: `AI_Evaluation_Report_[timestamp].xlsx`
3. Save to desired location

**Report Contents (7 Sheets):**

1. **Summary:**
   - Overall average scores
   - Statistical comparisons
   - Key insights
   - Winner declarations

2. **By Category:**
   - Performance breakdown by query type
   - Informational, Transactional, Comparative, etc.
   - Category-specific insights

3. **By Quality:**
   - Performance by query quality level
   - Well-formed vs Poorly-formed
   - Tests hypothesis about Google's advantage

4. **By Intent Clarity:**
   - Performance by intent clarity level
   - High vs Low clarity queries
   - Intent understanding correlation

5. **By Web Search:**
   - ChatGPT with vs without web search
   - Web search usage frequency
   - Impact analysis

6. **Raw Data:**
   - All queries with full responses
   - All scores
   - Complete dataset for custom analysis

7. **Individual Queries:**
   - Query-by-query comparison
   - Side-by-side scores
   - Detailed notes

### Step 2: Review Key Findings

Open the Excel file and navigate to **"Summary"** sheet.

**Look for:**
- Overall winner
- Largest performance gaps
- Statistical significance (if 200 queries scored)
- Category-specific winners
- Hypothesis validation (did Google excel on poorly-formed queries?)

### Step 3: Generate Visualizations

```bash
# Run the visualization script
python create_comparison_chart.py
```

**Generated files:**
- `comparison_chart.png`: Side-by-side comparison
- `detailed_comparison_chart.png`: Single detailed view

**Use these charts:**
- In presentations
- In blog posts
- In academic papers
- For social media sharing

### Step 4: Custom Analysis (Optional)

The application includes a Python analysis module for custom analysis:

```python
from analyzer import Analyzer
import json

# Load data
with open('results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Initialize analyzer
analyzer = Analyzer()

# Run custom analysis
stats = analyzer.calculate_statistics(results)
print(stats)
```

---

## Part 4: Troubleshooting

### Common Issues

#### Issue: "API Key Invalid"
**Solution:**
1. Check `.env` file exists
2. Verify API key starts with `sk-proj-`
3. No extra spaces or quotes
4. Key is active on OpenAI dashboard

#### Issue: "Rate Limit Exceeded"
**Solution:**
1. Wait 60 seconds
2. Reduce batch size (try 10 instead of 20)
3. Increase `rate_limit_delay` in `config.json`
4. Check OpenAI tier limits: [Rate Limits](https://platform.openai.com/account/rate-limits)

#### Issue: "No Google AI Response"
**Solution:**
1. Verify AI Mode is enabled for your account
2. Try different query (some queries don't trigger AI)
3. Check Google Labs: [labs.google.com](https://labs.google.com)
4. Try incognito/private browsing window

#### Issue: "Server Won't Start"
**Solution:**
1. Check port 5000 isn't already in use:
   - Windows: `netstat -ano | findstr :5000`
   - macOS/Linux: `lsof -i :5000`
2. Kill conflicting process
3. Or change port in `.env`: `FLASK_PORT=5001`

#### Issue: "Results Not Saving"
**Solution:**
1. Check write permissions in directory
2. Check disk space
3. Look for error messages in terminal
4. Check `results.json` file permissions

#### Issue: "Charts Won't Generate"
**Solution:**
1. Verify matplotlib installed: `pip install matplotlib`
2. Check `results.json` has scored queries
3. Check Python encoding (Windows users)
4. Try: `python -c "import matplotlib.pyplot as plt; print('OK')"`

### Getting Help

If you encounter issues not covered here:

1. **Check existing issues:** [GitHub Issues](https://github.com/aupsy/GoogleAIModeVSChatGPT/issues)
2. **Open new issue:** Include:
   - Error message (full text)
   - Python version
   - Operating system
   - Steps to reproduce
3. **Contact:** [Your contact info]

---

## Part 5: Customization

### Modify the Query Dataset

Edit `query_dataset.json`:

```json
{
  "201": {
    "id": 201,
    "query": "Your custom query here",
    "category": "informational",
    "quality": "well_formed",
    "intent_clarity": "high"
  }
}
```

**Fields:**
- `id`: Unique integer
- `query`: The actual query text
- `category`: informational, transactional, comparative, procedural, real_time, complex
- `quality`: well_formed, poorly_formed, ambiguous, typos_informal, time_sensitive
- `intent_clarity`: high, medium, low, very_low

### Change the Model

Edit `config.json`:

```json
{
  "model": "gpt-4-turbo",  // Change this
  ...
}
```

**Available models:**
- `gpt-4o-mini-search-preview` (with web search)
- `gpt-4-turbo`
- `gpt-4o`
- `gpt-3.5-turbo` (cheaper, lower quality)

### Add More Platforms

To compare additional platforms (Claude, Perplexity, etc.):

1. Add new response collection button in `templates/index.html`
2. Add new fields to scoring interface
3. Modify `analyzer.py` to include new platform
4. Update report generation in `report_generator.py`

(Detailed instructions for this are beyond scope, but the codebase is structured to make this straightforward)

---

## Part 6: Best Practices

### Data Collection
- ✅ Start with small batches (10-20 queries)
- ✅ Verify results look correct before large batches
- ✅ Take regular breaks to maintain consistency
- ✅ Save exports periodically as backups
- ✅ Document any unusual findings in notes field

### Scoring
- ✅ Review scoring rubric before starting
- ✅ Stay consistent (don't change criteria mid-study)
- ✅ Score in single session if possible (or limit sessions)
- ✅ Take breaks every 20-30 queries
- ✅ Use notes field for borderline cases

### Analysis
- ✅ Export report regularly (backups)
- ✅ Review outliers manually
- ✅ Consider statistical significance
- ✅ Acknowledge limitations in writeup
- ✅ Share methodology transparently

---

## Part 7: Timeline

**Estimated time breakdown for 200 queries:**

| Phase | Time | Type |
|-------|------|------|
| Setup | 15-30 min | One-time |
| ChatGPT Collection | 20 min | Automated |
| Google Collection | 1-1.5 hours | Manual |
| Scoring | 1-1.5 hours | Manual |
| Analysis | 15 min | Automated |
| **Total** | **~3-4 hours** | |

**Shorter studies:**
- 50 queries: ~1 hour total
- 100 queries: ~2 hours total

---

## Part 8: Cost Breakdown

**OpenAI API Costs** (as of January 2026):

| Queries | Estimated Cost |
|---------|----------------|
| 20 | $0.10-0.20 |
| 50 | $0.25-0.50 |
| 100 | $0.50-1.00 |
| 200 | $1.00-2.00 |

**Notes:**
- Costs vary by model
- Longer responses cost more
- Web search adds minimal cost
- Monitor: [OpenAI Usage](https://platform.openai.com/usage)

**Google AI Mode:** Free (standard Google Search access)

---

## Conclusion

You now have everything needed to reproduce the study! Follow the steps sequentially, and you'll have your own comprehensive AI comparison.

**Questions?** Open an issue: [GitHub Issues](https://github.com/aupsy/GoogleAIModeVSChatGPT/issues)

**Good luck with your research!** 🚀

---

*Last Updated: February 8, 2026*
