"""
Gemini-powered AI Copilot for MapMyNotes.
Provides summarization, reasoning, and PDF study companion generation.
"""

import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any
from fpdf import FPDF

# ----------------------------------------------------------------------
# 🔑 Gemini Setup
# ----------------------------------------------------------------------

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)
MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)


# ----------------------------------------------------------------------
# 🧠 Copilot Context and Core
# ----------------------------------------------------------------------

def init_copilot() -> List[Dict[str, Any]]:
    """Initialize conversation memory for context-aware responses."""
    return [
        {
            "role": "user",
            "parts": [
                "You are MapMyNotes Copilot — a helpful academic assistant. "
                "You receive study notes and mind map structures and respond "
                "clearly, concisely, and with examples."
            ]
        }
    ]


def _compose_context(map_meta: Dict[str, Any]) -> str:
    """Convert mind map metadata (nodes, summaries) into readable context."""
    if not map_meta:
        return "No map context provided."

    text_parts = []
    nodes = map_meta.get("nodes", [])
    if nodes:
        text_parts.append("Mind Map Topics:")
        for n in nodes[:50]:
            text_parts.append(f"- {n.get('label', '')}")

    if "sentences" in map_meta:
        text_parts.append("\nSource Text Highlights:")
        for s in map_meta["sentences"][:40]:
            text_parts.append(f"• {s}")

    summary = map_meta.get("summary") or ""
    if summary:
        text_parts.append("\nOverall Summary:\n" + summary)

    return "\n".join(text_parts)


# ----------------------------------------------------------------------
# 💬 Gemini Interaction
# ----------------------------------------------------------------------

def ask_copilot(question: str, history: List[Dict[str, Any]], map_meta: Dict[str, Any]) -> str:
    """Ask Gemini a question using the entire mind-map context."""
    context = _compose_context(map_meta)
    prompt = f"Context:\n{context}\n\nUser Question: {question}"
    history.append({"role": "user", "parts": [prompt]})

    try:
        response = model.generate_content(history)
        reply = response.text.strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    history.append({"role": "model", "parts": [reply]})
    return reply


def summarize_map(map_meta: Dict[str, Any]) -> str:
    """Generate a concise, bullet-style summary of the current mind map."""
    context = _compose_context(map_meta)
    prompt = (
        "Create a clear and concise summary of this mind map suitable for quick revision. "
        "Use bullet points and key ideas.\n\n" + context
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"
def generate_quiz_and_flashcards(summary_text: str):
    """
    Use Gemini to generate 5 flashcards and 5 quiz Q/A pairs
    from the given study summary or extracted text.
    Returns two lists: flashcards and quiz_items.
    """
    if not summary_text.strip():
        return [], []

    prompt = f"""
You are an academic assistant. Based on the text below, create:
1. 5 concise flashcards (front = question, back = answer)
2. 5 short quiz questions with 4 options each and the correct answer marked.

Return valid JSON:
{{
  "flashcards": [{{"q": "...", "a": "..."}}],
  "quiz": [{{"q": "...", "options": ["...","...","...","..."], "answer": "..."}}]
}}

Text:
{summary_text}
"""
    try:
        response = model.generate_content(prompt)
        import json
        data = json.loads(response.text)
        flashcards = data.get("flashcards", [])
        quiz = data.get("quiz", [])
        return flashcards, quiz
    except Exception as e:
        return [], []

# ----------------------------------------------------------------------
# 🎓 Node Explanation Utility
# ----------------------------------------------------------------------

def explain_node(node_text: str) -> str:
    """Simplify or elaborate a node concept."""
    prompt = f"Explain this topic in simple terms and give a short example:\n\n{node_text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"
    
def generate_quiz_and_flashcards(summary_text: str):
    """
    Uses Gemini to create short flashcards and quiz questions from the mind map summary.
    Returns (flashcards, quiz) lists.
    """
    if not summary_text.strip():
        return [], []

    prompt = f"""
    You are an academic NLP assistant. From the text below, create:
    1. 5 flashcards (question + concise answer)
    2. 5 multiple-choice quiz questions (with 4 options and the correct answer).

    Text:
    {summary_text}

    Output valid JSON:
    {{
      "flashcards": [{{"q": "...", "a": "..."}}],
      "quiz": [{{"q": "...", "options": ["A","B","C","D"], "answer": "A"}}]
    }}
    """
    try:
        response = model.generate_content(prompt)
        import json, re
        match = re.search(r'(\{.*\}|\[.*\])', response.text, re.S)
        if not match:
            return [], []
        data = json.loads(match.group(1))
        return data.get("flashcards", []), data.get("quiz", [])
    except Exception:
        return [], []

