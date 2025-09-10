# AI Study Planner

An interactive web application that helps users plan their studies and get instant answers using Gemini AI and DuckDuckGo web search. The app features a modern chat interface, Markdown rendering, and robust backend integration.

---

## Features

- **Conversational AI:** Powered by Gemini (Google Generative AI).
- **Web Search Integration:** Use `search:` or `/search` to trigger DuckDuckGo search.
- **Markdown Rendering:** Agent responses support Markdown formatting.
- **Typing Indicator:** Shows when the agent is responding.
- **Accessibility:** ARIA roles, labels, and keyboard support.
- **Security:** Sanitized Markdown output to prevent XSS.
- **Input Validation:** Limits message length and checks for empty input.
- **Production Ready:** CORS enabled, logging, and Gunicorn deployment support.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js (optional, for frontend build tools)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [DuckDuckGo Search Python Library](https://github.com/deedy5/duckduckgo-search)
- [Flask](https://flask.palletsprojects.com/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/pratikbarjatya/study-planner.git
   cd study-planner
   ```

2. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in `backend/`:
     ```
     GEMINI_API_KEY=your_google_gemini_api_key
     ```

4. **Run the Flask backend:**
   ```sh
   cd backend
   python app.py
   ```
   - For production:
     ```sh
     gunicorn -w 4 app:app
     ```

5. **Access the app:**
   - Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

- **Chat:** Type your study questions or topics.
- **Web Search:** Start your message with `search:` or `/search` to get web results.
  - Example: `search: quantum computing`
- **Markdown:** Agent responses may include formatted text, lists, and links.

---

## Project Structure

```
study-planner/
├── backend/
│   ├── app.py                # Flask backend
│   ├── gemini_client.py      # Gemini AI and DuckDuckGo integration
│   └── .env                  # API keys and secrets
├── templates/
│   └── index.html            # Frontend chat UI
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Security & Accessibility

- **Sanitization:** All Markdown output is sanitized using DOMPurify.
- **ARIA:** Chat history and messages use ARIA roles for screen readers.
- **Input Validation:** Both frontend and backend enforce message length and content checks.

---

## Customization

- **Change AI Model:** Edit `model_name` in `GeminiClient` (`gemini_client.py`).
- **Adjust Search Results:** Change `max_results` in `perform_web_search`.
- **Style:** Modify TailwindCSS classes in `index.html`.

---

## Troubleshooting

- **Gemini API Key Issues:** Ensure your `.env` file is present and correct.
- **DuckDuckGo Search Errors:** Check your internet connection and library installation.
- **CORS Errors:** Make sure Flask-CORS is installed and configured.

---

## License

MIT License

---

## Credits

- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [DuckDuckGo Search Python Library](https://github.com/deedy5/duckduckgo-search)
- [TailwindCSS](https://tailwindcss.com/)
- [Marked.js](https://marked.js.org/)
- [DOMPurify](https://github.com/cure53/DOMPurify)

---

## Contributing

Pull requests and suggestions are welcome! Please open an issue or submit a PR.