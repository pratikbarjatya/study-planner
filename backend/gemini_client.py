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

class GeminiClient:
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