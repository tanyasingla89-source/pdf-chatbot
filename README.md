# 📄 PDF Chatbot — Chat with any PDF using AI

A RAG-based document intelligence app that lets you upload any PDF and ask questions about it in natural language — powered by Google Gemini and FAISS.

## 🔴 Live Demo
👉 [https://pdf-chatbot-a5ua2wesnfs8d68n9duey6.streamlit.app](https://pdf-chatbot-a5ua2wesnfs8d68n9duey6.streamlit.app)

## 🧠 How it works (RAG Architecture)

```
PDF → Extract Text → Split into Chunks → Generate Embeddings
                                                ↓
User Question → Semantic Search → Relevant Chunks → Gemini AI → Answer
```

1. **PDF Processing** — Extracts and splits text into chunks
2. **Embeddings** — Converts chunks into vectors using Gemini Embedding API
3. **Vector Search** — FAISS finds the most relevant chunks for your question
4. **Generation** — Gemini 2.5 Flash generates accurate, grounded answers

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | Web UI |
| Google Gemini API | Embeddings + Answer generation |
| FAISS | Vector database for semantic search |
| PyPDF2 | PDF text extraction |

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/tanyasingla89-source/pdf-chatbot.git
cd pdf-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the app
streamlit run app.py
```

## 💡 Use Cases
- Chat with research papers
- Query legal documents
- Analyze annual reports
- Study from textbooks

## 📸 Screenshot
*Upload any PDF → Ask questions → Get instant answers*

## 🔮 Future Improvements
- [ ] Multi-document comparison
- [ ] Source page citation
- [ ] Chat history export
- [ ] Support for Word documents