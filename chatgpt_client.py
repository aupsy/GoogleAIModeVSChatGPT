"""
ChatGPT API Client Module
Handles all interactions with the OpenAI API including
single queries, batch processing, and rate limiting.
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ChatGPTClient:
    """Client for interacting with ChatGPT API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        """
        Initialize the ChatGPT client.

        Args:
            api_key: OpenAI API key (if None, loads from environment)
            model: Model to use for queries
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.rate_limit_delay = 1.0  # seconds between requests

        # Load config
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from config.json."""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'temperature': 0.7,
                'max_tokens': 2000,
                'rate_limit_delay': 1.0,
                'retry_attempts': 3,
                'retry_delay': 2.0
            }

    def query_chatgpt(self, query_text: str) -> Optional[Dict]:
        """
        Send a single query to ChatGPT and get response.

        Args:
            query_text: The question/query to send

        Returns:
            Dictionary with response data or None if failed
            Format: {
                'response': str,
                'model': str,
                'timestamp': str,
                'response_time_ms': float,
                'tokens_used': int,
                'finish_reason': str
            }
        """
        start_time = time.time()

        try:
            # Prepare API call parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. Provide comprehensive, accurate answers."},
                    {"role": "user", "content": query_text}
                ],
                "max_tokens": self.config.get('max_tokens', 2000)
            }

            # Add web search if using a search-enabled model
            if 'search' in self.model.lower():
                api_params['web_search_options'] = {}
                # Search models don't support temperature parameter
            else:
                # Only add temperature for non-search models
                api_params['temperature'] = self.config.get('temperature', 0.7)

            # Make API call
            response = self.client.chat.completions.create(**api_params)

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000

            # Extract response data
            result = {
                'response': response.choices[0].message.content,
                'model': response.model,
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': round(response_time_ms, 2),
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'finish_reason': response.choices[0].finish_reason
            }

            # Check if web search was used (indicated by annotations/citations)
            message = response.choices[0].message
            annotations = getattr(message, 'annotations', None)
            if annotations and len(annotations) > 0:
                result['web_search_used'] = True
                result['web_search_citations_count'] = len(annotations)
            else:
                result['web_search_used'] = False
                result['web_search_citations_count'] = 0

            return result

        except Exception as e:
            print(f"Error querying ChatGPT: {e}")
            return None

    def query_with_retry(self, query_text: str, max_attempts: Optional[int] = None) -> Optional[Dict]:
        """
        Query ChatGPT with retry logic for handling transient errors.

        Args:
            query_text: The question/query to send
            max_attempts: Maximum retry attempts (default from config)

        Returns:
            Response dictionary or None if all attempts fail
        """
        if max_attempts is None:
            max_attempts = self.config.get('retry_attempts', 3)

        retry_delay = self.config.get('retry_delay', 2.0)

        for attempt in range(max_attempts):
            try:
                result = self.query_chatgpt(query_text)
                if result is not None:
                    if attempt > 0:
                        print(f"Success on attempt {attempt + 1}")
                    return result

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")

                if attempt < max_attempts - 1:
                    # Exponential backoff
                    delay = retry_delay * (2 ** attempt)
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

        print(f"All {max_attempts} attempts failed for query")
        return None

    def batch_query(self, queries: List[Dict], callback=None) -> List[Dict]:
        """
        Process multiple queries in batch with rate limiting.

        Args:
            queries: List of query dictionaries (must have 'id' and 'query' keys)
            callback: Optional callback function called after each query
                     Signature: callback(current_index, total, query_id, result)

        Returns:
            List of result dictionaries with query_id and response data
        """
        results = []
        total = len(queries)

        print(f"Processing batch of {total} queries...")

        for idx, query in enumerate(queries):
            query_id = query.get('id')
            query_text = query.get('query')

            if not query_text:
                print(f"Skipping query {query_id}: missing query text")
                continue

            print(f"Query {idx + 1}/{total} (ID: {query_id})")

            # Query with retry
            result = self.query_with_retry(query_text)

            if result:
                results.append({
                    'query_id': query_id,
                    'success': True,
                    'data': result
                })
                print(f"  [OK] Success ({result['tokens_used']} tokens, {result['response_time_ms']}ms)")
            else:
                results.append({
                    'query_id': query_id,
                    'success': False,
                    'data': None,
                    'error': 'Failed after retries'
                })
                print(f"  [FAIL] Failed")

            # Call callback if provided
            if callback:
                callback(idx + 1, total, query_id, result)

            # Rate limiting (skip delay for last query)
            if idx < total - 1:
                time.sleep(self.config.get('rate_limit_delay', 1.0))

        print(f"\nBatch complete: {len([r for r in results if r['success']])} succeeded, "
              f"{len([r for r in results if not r['success']])} failed")

        return results

    def estimate_cost(self, num_queries: int, avg_tokens_per_query: int = 500) -> Dict:
        """
        Estimate API cost for a batch of queries.

        Args:
            num_queries: Number of queries
            avg_tokens_per_query: Estimated tokens per query (prompt + completion)

        Returns:
            Dictionary with cost estimates
        """
        # GPT-4-turbo pricing (as of late 2024)
        # Input: $10 per 1M tokens, Output: $30 per 1M tokens
        # Assume 50% input, 50% output for estimation
        input_cost_per_1m = 10.0
        output_cost_per_1m = 30.0

        total_tokens = num_queries * avg_tokens_per_query
        input_tokens = total_tokens * 0.4  # Prompt is usually shorter
        output_tokens = total_tokens * 0.6  # Response is usually longer

        input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_1m
        total_cost = input_cost + output_cost

        # Estimate time
        time_per_query = 2.0 + self.config.get('rate_limit_delay', 1.0)  # ~2s per query + delay
        total_time_seconds = num_queries * time_per_query
        total_time_minutes = total_time_seconds / 60

        return {
            'num_queries': num_queries,
            'estimated_total_tokens': int(total_tokens),
            'estimated_cost_usd': round(total_cost, 2),
            'estimated_time_minutes': round(total_time_minutes, 1),
            'model': self.model
        }


def test_client():
    """Test the ChatGPT client with a simple query."""
    print("Testing ChatGPT Client...\n")

    try:
        client = ChatGPTClient()

        # Test single query
        print("Testing single query...")
        test_query = "What is the capital of France?"
        result = client.query_chatgpt(test_query)

        if result:
            print(f"[OK] Query successful!")
            print(f"  Response: {result['response'][:100]}...")
            print(f"  Tokens: {result['tokens_used']}")
            print(f"  Time: {result['response_time_ms']}ms")
        else:
            print("[FAIL] Query failed")

        # Test cost estimation
        print("\nCost estimation for 200 queries:")
        estimate = client.estimate_cost(200)
        for key, value in estimate.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Create a .env file with OPENAI_API_KEY=your_key")
        print("2. Or set OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    test_client()
