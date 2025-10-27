<h1 align="center">🧠 MapMyNotes – AI-Powered NLP Study Companion</h1>

<p align="center">
  <b>Transform your study notes into interactive mind maps with AI-generated explanations, flashcards, and quizzes.</b><br>
  <i>Built using Streamlit · Google Gemini · D3.js</i>
</p>

---

## ✨ Overview

**MapMyNotes** is an intelligent **NLP-based study assistant** that converts your notes, PDFs, or presentations into **interactive mind maps**, complete with **AI-generated flashcards and quizzes** for revision.

It helps learners visualize, understand, and retain information efficiently — combining Natural Language Processing, visualization, and education technology into one seamless tool.

---

## 🚀 Key Features

| Feature | Description |
|----------|-------------|
| 🧩 **Text → Mind Map** | Upload notes (PDF, PPTX, or text) to generate a structured D3-based mind map. |
| 🧠 **Hierarchical Structuring** | Uses Gemini to extract key concepts and organize them across multiple levels. |
| 💬 **AI Explanations** | Hover over any node to see a layman + technical explanation. |
| 📚 **Flashcards & Quizzes** | Auto-generated Q&A for self-testing and revision. |
| 🎨 **Interactive UI** | Zoom, pan, and explore dynamic mind maps with smooth animations. |
| 📸 **Download as PNG** | Save your mind map locally in one click. |
| 🔁 **Regenerate Flashcards** | Get fresh questions anytime without losing your map. |
| 🌳 **Unlimited Depth** | Gemini dynamically decides topic hierarchy — no depth restrictions. |

---

## 🧩 Architecture & Workflow

### 🔹 1. Input Layer
Users can upload:
- 📄 **PDFs** (via `PyMuPDF`)
- 🖼️ **PPTX** (via `python-pptx`)
- 📝 **Plain Text**  
Text is extracted and preprocessed.

### 🔹 2. NLP Processing (`modules/pipeline.py`)
1. **Chunking & Summarization:** Large text is divided into smaller pieces and summarized by Gemini.  
2. **Hierarchy Extraction:** Gemini identifies key topics & subtopics via `STRUCTURE_PROMPT`.  
3. **Graph Creation:** Hierarchy converted into nodes & edges (`build_graph_from_hierarchy`).  
4. **Explanations:** Each node explained by `explain_node_in_layman()` (Gemini-generated).  
5. **Quiz Generation:** Using `MAP_SUMMARY_PROMPT`, a summary + quiz is created.  
6. **Keyword Extraction:** Top keywords extracted using frequency counts.

### 🔹 3. Visualization (`modules/visualize.py`)
- Renders **D3.js Mind Map** with color-coded nodes.
- Includes:
  - Hover explanations
  - Zoom/pan controls
  - PNG download button  

### 🔹 4. Smart Study Companion (`app.py`)
- Right panel shows:
  - AI-generated **flashcards**
  - **Quick quizzes** with answers & scoring  
- Regeneration button lets users get new flashcards on demand.

---

## 🧠 End-to-End Flow Diagram

[User Uploads File]
↓
[Text Extraction (PDF/PPTX/TXT)]
↓
[Gemini NLP Processing → Topics + Subtopics]
↓
[Hierarchy → Nodes + Edges]
↓
[D3 Visualization → Mind Map]
↓
[Hover AI Explanations]
↓
[Summary + Flashcards + Quiz]


---

## 🧰 Tech Stack

| Layer | Technologies Used |
|--------|-------------------|
| 🖥️ **Frontend** | Streamlit, HTML, CSS, D3.js |
| 🧩 **Visualization** | D3 Tree Layout, save-svg-as-png |
| 🧠 **NLP & AI** | Google Gemini (Text Summarization, Structuring, QA Generation) |
| 🐍 **Backend** | Python, dotenv, json, time, uuid |
| 📄 **Data Handling** | PyMuPDF (`fitz`), python-pptx |
| 🔍 **Text Analytics** | Tokenization, Keyword Frequency Analysis |
| 🔒 **Security** | .env-based API key management |

---

## 📚 Example Workflow
    A[User Uploads File] --> B(Text Extraction: PDF/PPTX/TXT);
    B --> C(Gemini NLP Processing: Topics + Subtopics);
    C --> D(Hierarchy → Nodes + Edges);
    D --> E(D3 Visualization → Mind Map);
    E --> F(Hover AI Explanations);
    D --> G(Summary + Flashcards + Quiz);
    E --> H(Download as PNG);

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```
git clone https://github.com/AvniBhardwaj1/MapMyNotes.git
cd MapMyNotes
⚙️ Installation & Setup
```
## 2️⃣ Create Virtual Environment
```
python -m venv venv
# macOS/Linux
source venv/bin/activate     
# Windows
venv\Scripts\activate
```
## 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```
## 4️⃣ Add Gemini API Key

Create a .env file in your project’s root directory and add:
```
GEMINI_API_KEY=your_api_key_here
```
## 5️⃣ Run the App
```
streamlit run app.py
```

## 🧠 NLP Concepts Demonstrated
🧩 Concept	💡 Description
🧹 Text Preprocessing	Cleaning, chunking, and token normalization
🧾 Summarization	Extractive + abstractive summarization via Gemini
🧱 Topic Extraction	Hierarchical semantic structuring
💬 Paraphrasing	Simplified layman + technical explanations for clarity
🧮 Keyword Extraction	Frequency and co-occurrence-based feature extraction
🎯 Question Generation	Auto-generated flashcards & quizzes from summarized content
🕸️ Graph Representation	Mind maps built from node–edge graph structure using D3.js


## 🌱 Future Enhancements
``` bash
“Innovation never stops — these are the next steps planned for MapMyNotes.”

🔹 1. Domain-Aware Learning

Automatically detect the subject domain (e.g., Medical, Engineering, Finance) to tailor explanations, tone, and quiz difficulty level according to the content.

🔹 2. Multi-Document Mapping

Allow uploading multiple documents at once to build cross-linked knowledge maps, showing how different concepts connect across topics.

🔹 3. Semantic Search

Integrate a vector-based semantic search (using Sentence-BERT or Word2Vec) to find related concepts within or across notes.

🔹 4. Voice Interaction

Enable speech-to-text and text-to-speech capabilities so learners can dictate notes and listen to AI-generated explanations hands-free.

🔹 5. Enhanced Mind Map Intelligence

Introduce auto-clustering and focus mode — automatically expand or collapse nodes based on their relevance or importance.

🔹 6. Cloud Integration

Allow users to save and sync generated mind maps to Google Drive, Firebase, or Notion for easy access and collaboration.

🔹 7. Study Analytics Dashboard

Develop a learning analytics dashboard that tracks user progress, quiz results, and study time to provide personalized recommendations.

🔹 8. AI Tutor Mode

Convert flashcards into an interactive chatbot tutor that explains concepts conversationally and guides users through difficult topics.
``` 
## 👩‍💻 Author

Avni Bhardwaj
🎓 B.Tech Computer Engineering – SVKM’s NMIMS, Indore
## 🧩 Acknowledgments
Special thanks to Google Gemini API for enabling advanced NLP and to Streamlit for providing an easy-to-use web framework.
<p align="center"> <i>“Transform your notes into knowledge — one mind map at a time.”</i><br><br> 🧠 Made with ❤️ by <b>Avni Bhardwaj</b> </p> ```
