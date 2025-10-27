# 🧠 MapMyNotes – AI-Powered NLP Study Companion

**MapMyNotes** is an intelligent, NLP-based study assistant that converts your notes, PDFs, or presentations into **interactive mind maps**, complete with **AI-generated flashcards and quizzes** for revision.

Built using **Streamlit**, **Google Gemini**, and **D3.js**, it’s designed to help students and learners visualize, understand, and retain study material more effectively.

---

## 🚀 Features

✅ **Text to Mind Map** – Upload any text, PDF, or PPTX, and the system generates an interactive D3-based mind map.  
✅ **Smart Hierarchical Structuring** – Uses Gemini to extract key topics and subtopics in a multi-level hierarchy.  
✅ **Layman + Technical Explanations** – Hover over nodes to get AI-generated explanations that simplify complex topics.  
✅ **Interactive Flashcards & Quizzes** – Automatically generates quick flashcards and multiple-choice quizzes for revision.  
✅ **Download Map as PNG** – Save your visualized map locally.  
✅ **Regenerate Flashcards Anytime** – Refresh questions without altering the mind map structure.  
✅ **Unlimited Node Depth** – Supports deep hierarchies as Gemini dynamically decides topic levels.

---

## 🧩 Architecture Overview

### 🔹 Input
- Upload **PDF**, **PPTX**, or **plain text**.
- Extracted using:
  - `PyMuPDF` (`fitz`) for PDFs
  - `python-pptx` for PPTX
  - Direct read for `.txt`

### 🔹 NLP Pipeline (`modules/pipeline.py`)
1. **Text Preprocessing & Chunking**
   - Large documents are split into manageable chunks.
   - Each chunk is summarized using Gemini.

2. **Topic Extraction & Hierarchy Generation**
   - Prompt (`STRUCTURE_PROMPT`) guides Gemini to identify key topics and organize them hierarchically.
   - Returns a JSON structure of topics, summaries, and subtopics.

3. **Graph Conversion**
   - JSON is converted into flat `nodes` and `edges` via `build_graph_from_hierarchy()`.

4. **AI Node Explanations**
   - Each topic node is explained using `explain_node_in_layman()` (from `hover_tooltip.py`).
   - Includes a simple explanation, technical context, and analogy.

5. **Summary + Quiz Generation**
   - Gemini produces a concise study summary, bullet points, and quiz questions (`MAP_SUMMARY_PROMPT`).

6. **Keyword Extraction**
   - Extracts top recurring words using frequency analysis (`collections.Counter`).

---

### 🔹 Visualization (`modules/visualize.py`)
- The hierarchical structure is rendered using **D3.js**.
- Each node is color-coded by depth and includes:
  - Topic name
  - Hover explanation tooltip (layman + technical)
- Supports **zoom**, **pan**, and **PNG download**.

---

### 🔹 Smart Study Companion (Right Panel in `app.py`)
- Displays **flashcards** and **quiz questions** derived from the generated summary.
- Option to **regenerate flashcards** dynamically.
- Full quiz mode with answer validation and scoring.

---

## 🧠 End-to-End Data Flow

| Step | File | Function | Description |
|------|------|-----------|--------------|
| 1️⃣ Input Extraction | `extract_text.py` | `extract_from_pdf/pptx/text()` | Extracts text from uploaded file |
| 2️⃣ NLP Processing | `pipeline.py` | `process_text_to_mindmap()` | Summarizes and extracts topic hierarchy |
| 3️⃣ Graph Building | `pipeline.py` | `build_graph_from_hierarchy()` | Converts hierarchy → nodes + edges |
| 4️⃣ Explanations | `hover_tooltip.py` | `explain_node_in_layman()` | AI explanation for hover tooltips |
| 5️⃣ Visualization | `visualize.py` | `visualize_graph()` | D3 mind map rendering |
| 6️⃣ Quiz & Flashcards | `copilot.py` / `app.py` | `generate_quiz_and_flashcards()` | Generates Q&A from summary |
| 7️⃣ UI Rendering | `app.py` | Streamlit components | Displays everything interactively |

---

## 🧰 Tech Stack

**Frontend & Visualization**
- 🧩 Streamlit  
- 🎨 D3.js  
- 🖼️ save-svg-as-png (for downloads)

**Backend & NLP**
- 🤖 Google Gemini (Text Summarization, Hierarchical Structuring, Question Generation)
- 🧠 Python (Text Processing, Keyword Extraction)
- 📄 PyMuPDF (`fitz`) and python-pptx (for text extraction)
- 🌿 dotenv (for API key security)

**Data Representation**
- JSON-based hierarchical knowledge graphs
- Graph → Node + Edge conversion → Mind map visualization

---

## 📚 Example Workflow

1. **Upload a PDF or Paste Text**
   > Example: “Introduction to Artificial Intelligence”

2. **Processing**
   - Gemini analyzes and extracts hierarchical structure:
     ```
     Artificial Intelligence
     ├── Machine Learning
     │   ├── Supervised Learning
     │   └── Unsupervised Learning
     ├── Natural Language Processing
     └── Robotics
     ```
3. **Visualization**
   - D3 mind map appears interactively.

4. **Hover**
   - Hover over “Machine Learning” →  
     *“In simple terms, ML enables systems to learn from data…”*

5. **Flashcards & Quiz**
   - Q: *What is the goal of Machine Learning?*  
     A: *To enable systems to improve automatically through data experience.*

6. **Download**
   - Click 📸 *Download Mind Map (PNG)*

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/AvniBhardwaj1/MapMyNotes.git
cd MapMyNotes
