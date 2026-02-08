"""
LLM-as-Judge Module
Uses ChatGPT (GPT-4o) to automatically evaluate and score responses from ChatGPT and Google AI Mode.
"""

import os
import json
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMJudge:
    """GPT-4o-based judge for evaluating AI responses."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM judge with OpenAI API."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Using GPT-4o as judge (different from gpt-4o-mini-search-preview)

    def evaluate_response(
        self,
        query: str,
        response: str,
        query_metadata: Dict
    ) -> Dict:
        """
        Evaluate a single response using Claude.

        Args:
            query: The original user query
            response: The AI's response to evaluate
            query_metadata: Dict with category, quality, intent_clarity

        Returns:
            Dict with scores: {
                'relevance': int (1-5),
                'completeness': int (1-5),
                'source_quality': int (1-5),  # Now evaluates "Clarity"
                'intent_understood': bool,
                'followups_needed': bool
            }
        """
        evaluation_prompt = f"""You are an expert evaluator of AI assistant responses. Evaluate the following response on these criteria:

**Original Query:** {query}

**Query Metadata:**
- Category: {query_metadata.get('category', 'Unknown')}
- Query Quality: {query_metadata.get('quality', 'Unknown')}
- Intent Clarity: {query_metadata.get('intent_clarity', 'Unknown')}

**Response to Evaluate:**
{response}

---

**Evaluation Criteria:**

1. **Relevance (1-5):** How well does the response address the query?
   - 1: Not relevant at all
   - 3: Somewhat relevant
   - 5: Directly and fully relevant

2. **Completeness (1-5):** How thorough and complete is the answer?
   - 1: Incomplete, missing key information
   - 3: Adequate, covers main points
   - 5: Comprehensive, covers all aspects

3. **Clarity (1-5):** How clear, well-structured, and easy to understand is the response?
   - 1: Confusing, poorly organized, hard to follow
   - 3: Reasonably clear, some organization
   - 5: Crystal clear, excellently structured, very easy to understand

4. **Intent Understood (Yes/No):** Did the AI correctly understand what the user was asking for?

5. **Follow-ups Needed (Yes/No):** Would the user likely need to ask follow-up questions to get a satisfactory answer?

**Response Format:**
Return ONLY a JSON object with your evaluation:
{{
  "relevance": <1-5>,
  "completeness": <1-5>,
  "source_quality": <1-5>,
  "intent_understood": <true/false>,
  "followups_needed": <true/false>,
  "reasoning": "<brief 1-2 sentence explanation>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,  # Lower temperature for more consistent scoring
                messages=[
                    {"role": "system", "content": "You are an objective expert evaluator of AI assistant responses. Provide fair, unbiased assessments based on the given criteria."},
                    {"role": "user", "content": evaluation_prompt}
                ]
            )

            # Extract the response text
            response_text = response.choices[0].message.content.strip()

            # Parse JSON (might have markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            evaluation = json.loads(response_text)

            # Handle both 'source_quality' and 'clarity' field names for backward compatibility
            clarity_score = evaluation.get('source_quality') or evaluation.get('clarity', 3)

            return {
                'relevance': evaluation['relevance'],
                'completeness': evaluation['completeness'],
                'source_quality': clarity_score,  # Now represents Clarity score
                'intent_understood': evaluation['intent_understood'],
                'followups_needed': evaluation['followups_needed'],
                'reasoning': evaluation.get('reasoning', '')
            }

        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            if 'evaluation' in locals():
                print(f"Evaluation JSON keys: {list(evaluation.keys())}")
            if 'response_text' in locals():
                print(f"Response text: {response_text[:200]}...")
            return None

    def compare_responses(
        self,
        query: str,
        chatgpt_response: str,
        google_response: str,
        query_metadata: Dict
    ) -> Dict:
        """
        Evaluate and compare both ChatGPT and Google AI responses.

        Returns:
            Dict with both evaluations: {
                'chatgpt': {...scores...},
                'google': {...scores...}
            }
        """
        print(f"Evaluating responses for query: {query[:50]}...")

        chatgpt_scores = self.evaluate_response(query, chatgpt_response, query_metadata)
        google_scores = self.evaluate_response(query, google_response, query_metadata)

        return {
            'chatgpt': chatgpt_scores,
            'google': google_scores
        }

    def estimate_cost(self, num_queries: int) -> Dict:
        """
        Estimate cost for evaluating queries.

        GPT-4o pricing (as of 2025):
        - Input: $2.50 per 1M tokens
        - Output: $10 per 1M tokens

        Args:
            num_queries: Number of query pairs to evaluate

        Returns:
            Dict with cost estimates
        """
        # Rough estimates:
        # - Prompt: ~400 tokens
        # - Response: ~150 tokens
        # - Per query pair: 2 evaluations

        tokens_per_evaluation = 550
        evaluations = num_queries * 2  # Both ChatGPT and Google

        total_input_tokens = evaluations * 400
        total_output_tokens = evaluations * 150

        input_cost = (total_input_tokens / 1_000_000) * 2.50
        output_cost = (total_output_tokens / 1_000_000) * 10.0
        total_cost = input_cost + output_cost

        # Time estimate: ~2 seconds per evaluation
        time_minutes = (evaluations * 2) / 60

        return {
            'num_queries': num_queries,
            'total_evaluations': evaluations,
            'estimated_total_tokens': total_input_tokens + total_output_tokens,
            'estimated_cost_usd': round(total_cost, 2),
            'estimated_time_minutes': round(time_minutes, 1),
            'model': self.model
        }


def test_judge():
    """Test the LLM judge with a sample query."""
    print("Testing LLM Judge...\n")

    try:
        judge = LLMJudge()

        # Test evaluation
        test_query = "What is the capital of France?"
        test_response = "The capital of France is Paris. It is located in the north-central part of the country."
        test_metadata = {
            'category': 'Informational',
            'quality': 'Well-formed',
            'intent_clarity': 'High'
        }

        print("Evaluating test response...")
        scores = judge.evaluate_response(test_query, test_response, test_metadata)

        if scores:
            print("[OK] Evaluation successful!")
            print(f"Scores: {json.dumps(scores, indent=2)}")
        else:
            print("[FAIL] Evaluation failed")

        # Cost estimation
        print("\nCost estimation for 180 queries (200 - 20 manual):")
        estimate = judge.estimate_cost(180)
        for key, value in estimate.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure your OPENAI_API_KEY is set in .env file")


if __name__ == "__main__":
    test_judge()
