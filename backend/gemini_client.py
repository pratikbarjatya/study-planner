import os
import logging
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()

def perform_web_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """
    Performs a DuckDuckGo web search for the given query and returns a list of search results.

    Args:
        query (str): The search query string.
        max_results (int, optional): Maximum number of results to return. Defaults to 6.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing 'title', 'href', and 'body' keys
        representing the search result's title, URL, and a brief snippet of the body text.

    Notes:
        - The body text is truncated to 300 characters for brevity.
        - If an error occurs during the search, an empty list is returned and the error is logged.
    """
    """Perform a DuckDuckGo search and return a list of results (title, href, body)."""
    results: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                if not isinstance(result, dict):
                    continue
                title = result.get('title', '')
                href = result.get('href', '')
                body = result.get('body', '')
                if title and href:
                    # Limit body length for prompt brevity
                    body = body[:300] + ('...' if len(body) > 300 else '')
                    results.append({'title': title, 'href': href, 'body': body})
        return results
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return []

"""
This module provides a GeminiClient class for interacting with Google's Gemini generative AI model,
with optional integration of DuckDuckGo web search results to enhance responses. It includes:

Functions:
----------
- perform_web_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    Performs a DuckDuckGo search for the given query and returns a list of results containing
    title, href, and body. Handles errors gracefully and limits body length for brevity.

Classes:
--------
- GeminiClient:
    A client for Google's Gemini generative AI model. Supports normal chat and enhanced responses
    using real-time web search results when triggered by specific user input patterns ("search:" or "/search ").
    - __init__(api_key: str = None, model_name: str = 'gemini-1.5-flash'):
        Initializes the GeminiClient with the provided API key and model name.
        Configures the generative model and prepares chat history.
    - generate_response(user_input: str) -> str:
        Generates an AI response to the user input. If the input triggers a web search,
        performs the search, composes a context with numbered references, and instructs the AI
        to cite sources inline. Otherwise, responds as a normal chat.

Logging:
--------
- Uses Python's logging module to report errors and configuration issues.

Environment:
------------
- Loads environment variables using dotenv for API key management.

Dependencies:
-------------
- google.generativeai
- duckduckgo_search
- python-dotenv
"""
class GeminiClient:
    """Client for interacting with the Gemini AI model, with optional web search integration."""
    def __init__(self, api_key: str = None, model_name: str = 'gemini-1.5-flash'):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY is not set.")
            self.chat = None
            return
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            self.chat = None

    def generate_response(self, user_input: str) -> str:
        """Generate an AI response, optionally using web search if triggered."""
        if not self.chat:
            return "AI service is not configured correctly."

        try:
            text = user_input or ""
            lower = text.strip().lower()

            # Search trigger (case-insensitive, flexible)
            search_query = None
            if lower.startswith("search:"):
                search_query = text.split(":", 1)[1].strip()
            elif lower.startswith("/search "):
                search_query = text.split(" ", 1)[1].strip()

            if search_query:
                web_results = perform_web_search(search_query, max_results=6)
                if not web_results:
                    return "I could not retrieve web results right now. Please try again."

                # Build context with numbered references, escape Markdown-sensitive chars
                refs_lines = []
                for idx, item in enumerate(web_results, start=1):
                    title = item['title'].replace('[', '\\[').replace(']', '\\]')
                    body = item['body'].replace('[', '\\[').replace(']', '\\]')
                    refs_lines.append(f"[{idx}] {title} — {item['href']}\n{body}")
                refs_block = "\n\n".join(refs_lines)

                system_prompt = (
                    "You are an AI research assistant. Use the provided web search results to answer the user query. "
                    "Synthesize concisely, cite sources inline like [1], [2] where relevant, and include a brief summary."
                )
                composed = (
                    f"<system>\n{system_prompt}\n</system>\n"
                    f"<user_query>\n{search_query}\n</user_query>\n"
                    f"<web_results>\n{refs_block}\n</web_results>"
                )
                response = self.chat.send_message(composed)
                return response.text

            # Default: normal chat
            response = self.chat.send_message(text)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error while processing your request."