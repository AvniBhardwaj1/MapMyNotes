# app.py – MapMyNotes (Final Polished Version)
import os
import json
import streamlit as st
from dotenv import load_dotenv

# --- Local Imports ---
from modules.extract_text import extract_from_pdf, extract_from_pptx, extract_from_text
from modules.pipeline import process_text_to_mindmap
from modules.visualize import visualize_graph
# --- Initialize session state safely ---
if "map_data" not in st.session_state:
    st.session_state["map_data"] = None

if "map_meta" not in st.session_state:
    st.session_state["map_meta"] = {}

# --- Streamlit Setup ---
st.set_page_config(
    page_title="MapMyNotes – AI Mind Map Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Environment ---
load_dotenv()

# -------------------- PAGE HEADER --------------------
st.markdown("""
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #2b2d42;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #4a4e69;
            margin-bottom: 1.2rem;
        }
        .stButton>button {
            background-color: #4a90e2 !important;
            color: white !important;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.6em 1.2em;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2563eb !important;
            transform: scale(1.03);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🧠 MapMyNotes – AI-Powered Mind Map</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform your notes, PDFs, or slides into interactive mind maps and smart summaries.</p>", unsafe_allow_html=True)

# ----------------------- INPUT SECTION -----------------------
st.sidebar.header("📥 Upload / Enter Study Material")

input_mode = st.sidebar.radio(
    "Choose Input Type:",
    ["Paste Text", "Upload PDF", "Upload PPTX"],
    horizontal=False
)

text_data = ""

if input_mode == "Paste Text":
    text_data = st.text_area("✍️ Paste your study text here:", height=200)
elif input_mode == "Upload PDF":
    pdf_file = st.file_uploader("📄 Upload PDF", type=["pdf"])
    if pdf_file:
        text_data = extract_from_pdf(pdf_file)
elif input_mode == "Upload PPTX":
    pptx_file = st.file_uploader("📊 Upload PPTX", type=["pptx"])
    if pptx_file:
        text_data = extract_from_pptx(pptx_file)

st.sidebar.info("💡 Tip: You can also paste lecture notes or copy text from slides to generate your map.")

# ----------------------- GENERATE BUTTON -----------------------
st.markdown("---")
generate_btn = st.button("🚀 Generate Mind Map", use_container_width=True)

if generate_btn:
    if not text_data.strip():
        st.error("⚠️ Please enter or upload some text first.")
        st.stop()

    with st.spinner("🧩 Processing your notes into a structured mind map..."):
        st.write("Extracted text length:", len(text_data))
        mm = process_text_to_mindmap(text_data)
        if "error" in mm.get("meta", {}):
            st.error(f"Gemini Error: {mm['meta']['error']}")

        data = {"nodes": mm["nodes"], "edges": mm["edges"]}
        meta = mm["meta"]

        st.session_state["map_data"] = data
        st.session_state["map_meta"] = meta
        st.success("✅ Mind map generated successfully!")

# ----------------------- DISPLAY SECTION -----------------------
if "map_data" in st.session_state and st.session_state["map_data"]:
    st.divider()
    col1, col2 = st.columns([2.5, 1.0], gap="large")

# --- Two-column layout for visualization and companion ---
col1, col2 = st.columns([2.4, 1.0], gap="large")

# --- LEFT COLUMN: Mind Map Visualization ---
with col1:
    st.subheader("🗺️ Generated Mind Map")
    st.caption("Drag, zoom, and hover nodes to explore relationships between topics.")
    data = st.session_state["map_data"]
    visualize_graph(data, title="MapMyNotes – Mind Map", height=720, width=1400)

# --- RIGHT COLUMN: Smart Study Companion (replace your existing with-col2 block) ---
with col2:
    st.subheader("📚 Smart Study Companion")
    st.markdown(
        "<p style='font-size:14px;color:#444'>"
        "Smart flashcards and a quick quiz generated from the mind map summary. "
        "Open the full quiz to take the test in full-width mode."
        "</p>",
        unsafe_allow_html=True,
    )

    meta = st.session_state.get("map_meta", {})
    summary_text = meta.get("summary", "")

    if not summary_text:
        st.info("💡 Generate a mind map first to view flashcards and quizzes.")
    else:
        # Lazily import generator (copilot.generate_quiz_and_flashcards should exist)
        from modules.copilot import generate_quiz_and_flashcards

        # Generate once and cache in session state
        if "smart_quiz_data" not in st.session_state:
            with st.spinner("🤖 Generating flashcards and quiz..."):
                flashcards, quiz = generate_quiz_and_flashcards(summary_text)
                # ensure data shapes
                st.session_state["smart_quiz_data"] = {
                    "flashcards": flashcards or [],
                    "quiz": quiz or []
                }
        else:
            flashcards = st.session_state["smart_quiz_data"]["flashcards"]
            quiz = st.session_state["smart_quiz_data"]["quiz"]

        # --- Flashcards (compact) ---
        if flashcards:
            st.markdown("#### 🗂️ Flashcards (click to reveal)")
            for i, card in enumerate(flashcards, 1):
                # Expanders keep the right column tidy
                with st.expander(f"Flashcard {i}: {card.get('q','Question')}"):
                    st.write(card.get("a", "No answer provided."))

        # --- Quick quiz preview / controls ---
        st.markdown("#### 🎯 Quick Quiz Preview")
        st.write("Take the mini-quiz inline or open the full quiz page for a cleaner experience.")

        # Button to open full-screen quiz area below the map
        if st.button("Open Full Quiz"):
            # Flag to show quiz full width beneath the map (handled later in the main layout)
            st.session_state["show_quiz_full"] = True
            st.rerun()

# --- Render full-width quiz if requested (place this after your display section) ---
def render_full_quiz(quiz_items):
    """
    Renders the quiz full-width. Does NOT auto-evaluate.
    Users must press 'Submit Answers' to validate.
    """
    if not quiz_items:
        st.info("No quiz found. Generate a mind map first.")
        return

    st.markdown("## 📝 Full Quiz — Test Yourself")
    st.markdown("Select an answer for each question (there is a Submit button at the end).")

    # Initialize state containers
    if "quiz_answers" not in st.session_state:
        st.session_state["quiz_answers"] = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = False
    if "quiz_score" not in st.session_state:
        st.session_state["quiz_score"] = None

    # Render questions with an explicit "Choose..." placeholder as the first option
    for idx, q in enumerate(quiz_items, start=1):
        q_key = f"q_{idx}"
        question_text = q.get("q", "Question text missing")
        options = q.get("options", [])  # expected: list like ["A","B","C","D"]
        answer = q.get("answer")  # expected: exact string of the correct option

        # Build choices with placeholder first to avoid default selection
        choices = ["— Select an answer —"] + options

        # Keep previously selected answer if present (persisted in session_state)
        selected = st.selectbox(f"Q{idx}. {question_text}", choices, key=q_key, index=0)

        # store selection (only meaningful when not placeholder)
        if selected != "— Select an answer —":
            st.session_state["quiz_answers"][q_key] = selected
        else:
            # ensure missing entries are not present
            st.session_state["quiz_answers"].pop(q_key, None)

        # Show answer feedback only after submission (prevent spoilage)
        if st.session_state.get("quiz_submitted"):
            user_choice = st.session_state.get("quiz_answers", {}).get(q_key)
            if user_choice:
                if user_choice == answer:
                    st.success(f"✅ Q{idx} Correct")
                else:
                    st.error(f"❌ Q{idx} Wrong — Correct: {answer}")
            else:
                st.warning(f"❗ Q{idx} Not answered — Correct: {answer}")

    # Submit button to validate answers
    if st.button("Submit Answers"):
        # Evaluate
        correct = 0
        total = len(quiz_items)
        for i, q in enumerate(quiz_items, start=1):
            key = f"q_{i}"
            user = st.session_state.get("quiz_answers", {}).get(key)
            if user is not None and user == q.get("answer"):
                correct += 1
        st.session_state["quiz_score"] = (correct, total)
        st.session_state["quiz_submitted"] = True
        st.success(f"Score: {correct} / {total}")

    # Allow reset / try again
    if st.session_state.get("quiz_submitted"):
        if st.button("Reset Quiz"):
            st.session_state["quiz_answers"] = {}
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_score"] = None
            st.rerun()


# --- If 'show_quiz_full' is set, render the full quiz below the map (full width) ---
if st.session_state.get("show_quiz_full"):
    quiz_items = st.session_state.get("smart_quiz_data", {}).get("quiz", [])
    # render inside a full-width container so it looks like a "page"
    st.divider()
    render_full_quiz(quiz_items)
    # Add a button to close the full quiz page
    if st.button("Close Quiz and Return to Map"):
        st.session_state["show_quiz_full"] = False
        st.rerun()


# ----------------------- FOOTER -----------------------
st.divider()
st.markdown(
    """
    <center style='color:gray;font-size:13px;'>
    🧩 Built with ❤️ by <b>Avni Bhardwaj</b> — Powered by NLP concepts & <b>Google Gemini</b><br>
    </center>
    """,
    unsafe_allow_html=True,
)
