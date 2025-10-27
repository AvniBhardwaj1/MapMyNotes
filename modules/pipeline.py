"""
pipeline.py — Text → Mind Map Generator (Enhanced Root Naming + AI Explanations)
-------------------------------------------------------------------------------
Converts raw study text into a hierarchical JSON structure for MapMyNotes.

✅ Unlimited hierarchy depth (Gemini decides number of nodes)
✅ Root node auto-titled by Gemini (main topic/theme)
✅ Gemini-2.5-flash optimized prompts
✅ Safe JSON parsing + fallback
✅ Batched AI explanations for hover tooltips
✅ Auto-generated study summary + quiz
"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------- Setup ----------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not set in .env")
genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"
MODEL = genai.GenerativeModel(MODEL_NAME)


# ---------------- Utility Functions ----------------

def _short_id(prefix="n"):
    """Generate short unique node IDs."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _safe_json_loads(s: str) -> Optional[Any]:
    """Safely parse possibly messy JSON output from Gemini."""
    try:
        return json.loads(s)
    except Exception:
        import re
        m = re.search(r'(\{.*\}|\[.*\])', s, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
        return None


def _call_gemini(prompt: str, retry: int = 1) -> str:
    """Call Gemini model with retry mechanism."""
    for attempt in range(retry + 1):
        try:
            resp = MODEL.generate_content(prompt)
            text = getattr(resp, "text", None) or str(resp)
            return text.strip()
        except Exception as e:
            if attempt < retry:
                time.sleep(1.2 * (attempt + 1))
                continue
            return f"__GEMINI_ERROR__: {e}"


# ---------------- Prompts ----------------

STRUCTURE_PROMPT = """
You are an expert educational AI that converts study material into a detailed mind map.

INPUT TEXT:
{text}

TASK:
- Identify key topics and organize them hierarchically.
- There can be multiple levels (like 3, 4, or more) if the content naturally supports it.
- Each node must include:
  • "title": short descriptive name (2–6 words)
  • "summary": a concise explanation (<= 40 words)
  • "key_points": 1–4 short bullet points (optional)
  • "subtopics": a list of deeper related nodes (if applicable)

OUTPUT:
Return strictly valid JSON with the structure:
[
  {{
    "title": "Root Topic",
    "summary": "...",
    "key_points": ["point1", "point2"],
    "subtopics": [
      {{
        "title": "Subtopic 1",
        "summary": "...",
        "key_points": ["p1", "p2"],
        "subtopics": [ ... ]
      }}
    ]
  }}
]
"""


MAP_SUMMARY_PROMPT = """
You are an academic summarizer. Given the structured hierarchy of a mind map, 
generate a short, clear study summary in JSON format.

Input (hierarchy JSON):
{hierarchy}

Return valid JSON:
{{
  "thesis": "1-line overall takeaway",
  "bullets": ["6 quick revision points"],
  "quiz": [
    {{"q": "Question 1?", "a": "Answer"}},
    {{"q": "Question 2?", "a": "Answer"}}
  ]
}}
"""


ROOT_NAME_PROMPT = """
You are given a block of study material.
Generate a short, descriptive title (max 6 words) that represents the main theme or subject.
Return only the title — no explanation.

Input text:
{text}
"""


# ---------------- Recursive Graph Builder ----------------

def build_graph_from_hierarchy(hierarchy, parent_id=None, level=0, nodes=None, edges=None):
    """Recursively convert nested hierarchy JSON from Gemini into flat nodes + edges."""
    if nodes is None:
        nodes, edges = [], []

    for item in hierarchy:
        node_id = _short_id(f"n{level}")
        label = item.get("title", "")[:140]
        summary = item.get("summary", "")[:400]
        key_points = item.get("key_points", [])[:6]
        subtopics = item.get("subtopics", [])

        nodes.append({
            "id": node_id,
            "label": label,
            "level": level,
            "summary": summary,
            "key_points": key_points
        })

        if parent_id:
            edges.append({"source": parent_id, "target": node_id})

        if isinstance(subtopics, list) and subtopics:
            build_graph_from_hierarchy(subtopics, node_id, level + 1, nodes, edges)

    return nodes, edges


# ---------------- Main Pipeline ----------------

def process_text_to_mindmap(text: str,
                            chunk_threshold_chars: int = 18000,
                            enable_map_summary: bool = True) -> Dict[str, Any]:
    """
    Convert raw text into a multi-level mind map (nodes + edges + metadata)
    using Gemini — with unlimited depth and pre-computed explanations.
    """

    text = (text or "").strip()
    if not text:
        return {"nodes": [], "edges": [], "meta": {"summary": "", "error": "no_text"}}

    # --- Summarize if text is too long ---
    if len(text) > chunk_threshold_chars:
        chunks = [text[i:i + chunk_threshold_chars] for i in range(0, len(text), chunk_threshold_chars)]
        summaries = []
        for c in chunks:
            p = f"Summarize this text in one short sentence (<=25 words):\n\n{c}"
            out = _call_gemini(p)
            summaries.append(out.splitlines()[0].strip())
        prompt_text = "\n".join(summaries)
    else:
        prompt_text = text

    # --- Generate Root Title ---
    root_prompt = ROOT_NAME_PROMPT.format(text=prompt_text)
    root_title = _call_gemini(root_prompt).splitlines()[0].strip()

    # --- Build Hierarchical Structure ---
    structure_prompt = STRUCTURE_PROMPT.format(text=prompt_text)
    raw_structure = _call_gemini(structure_prompt)
    structure = _safe_json_loads(raw_structure)

    if not structure or not isinstance(structure, list):
        retry_prompt = f"{structure_prompt}\n\nRe-output strictly valid JSON with nested subtopics only."
        structure = _safe_json_loads(_call_gemini(retry_prompt))

    if not structure:
        root_id = _short_id("root")
        node = {"id": root_id, "label": root_title or "Main Topic", "level": 0, "summary": text[:320]}
        return {"nodes": [node], "edges": [], "meta": {"summary": text[:800], "warning": "parse_failed"}}

    # --- Convert hierarchy → nodes + edges ---
    nodes, edges = build_graph_from_hierarchy(structure)
    meta = {"n_nodes": len(nodes)}

    # --- Generate Study Summary + Quiz ---
    if enable_map_summary:
        try:
            compact = json.dumps(structure[:3])
            map_prompt = MAP_SUMMARY_PROMPT.format(hierarchy=compact)
            raw_map = _call_gemini(map_prompt)
            parsed_map = _safe_json_loads(raw_map)
            if parsed_map:
                meta["summary"] = parsed_map.get("thesis", "") + "\n\n" + "\n".join(parsed_map.get("bullets", []))
                meta["quiz"] = parsed_map.get("quiz", [])
        except Exception as e:
            meta["summary_error"] = str(e)

    # --- Batched AI Explanations (for hover tooltips) ---
    try:
        titles = [n.get("label", "").strip() for n in nodes if n.get("label", "").strip()]
        if titles:
            batch_prompt = (
                "You are an AI educator. Given a list of study topics, return a JSON array where "
                "each item is {\"title\": \"topic\", \"explanation\": \"Layman + Technical + Tip (max 90 words)\"}.\n\n"
                "Topics:\n" + "\n".join(f"- {t}" for t in titles)
            )
            raw_expl = _call_gemini(batch_prompt)
            parsed = _safe_json_loads(raw_expl)

            mapping = {}
            if isinstance(parsed, list):
                for i in parsed:
                    k = (i.get("title") or "").strip()
                    mapping[k] = i.get("explanation") or ""
            elif isinstance(parsed, dict):
                for k, v in parsed.items():
                    mapping[k.strip()] = v

            for n in nodes:
                lbl = n.get("label", "").strip()
                n["ai_explanation"] = mapping.get(lbl, "No explanation available.")
        else:
            for n in nodes:
                n["ai_explanation"] = "No explanation available."
    except Exception as e:
        for n in nodes:
            n["ai_explanation"] = "Explanation unavailable."
        meta["tooltip_error"] = str(e)

    # --- Extract Keywords ---
    try:
        text_pool = " ".join(n.get("label", "") + " " + n.get("summary", "") for n in nodes)
        words = [w.lower().strip(".,:;()[]") for w in text_pool.split() if len(w) > 3]
        from collections import Counter
        meta["keywords"] = [w for w, _ in Counter(words).most_common(12)]
    except Exception:
        meta["keywords"] = []

    return {"nodes": nodes, "edges": edges, "meta": meta}
