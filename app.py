import streamlit as st
from pdf_processor import process_pdf, get_answer
import os

# --- Page Config ---
st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="📄",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0; }
    .footer { text-align: center; color: gray; font-size: 12px; padding-top: 2rem; }
    .source-box {
        background-color: #f0f9ff;
        border-left: 3px solid #0ea5e9;
        padding: 8px 12px;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 13px;
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class='main-header'>
    <h1>📄 PDF Chatbot</h1>
    <p>Upload any PDF and chat with it using AI — powered by RAG + Google Gemini</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/pdf.png", width=60)
    st.title("⚙️ Setup")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")

    st.markdown("---")
    st.markdown("### 📂 Upload Document")

    # Sample PDF option
    use_sample = st.checkbox("Use sample PDF (no upload needed)", value=False)

    if use_sample:
        st.info("📘 Using built-in sample PDF")
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            st.info(f"📊 Size: {round(uploaded_file.size/1024, 1)} KB")

    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("- *Summarize this document*")
    st.markdown("- *What are the key points?*")
    st.markdown("- *What is mentioned about accessibility?*")

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Process PDF ---
def load_pdf_source(use_sample, uploaded_file, api_key):
    if use_sample:
        sample_path = os.path.join(os.path.dirname(__file__), "sample.pdf")
        with open(sample_path, "rb") as f:
            return process_pdf(f, api_key), "sample.pdf"
    elif uploaded_file:
        return process_pdf(uploaded_file, api_key), uploaded_file.name
    return None, None

if api_key and (use_sample or uploaded_file):
    file_key = "sample.pdf" if use_sample else uploaded_file.name
    if "vector_store" not in st.session_state or st.session_state.get("file_name") != file_key:
        with st.spinner("🔍 Reading and indexing your PDF..."):
            vector_store, fname = load_pdf_source(use_sample, uploaded_file, api_key)
            st.session_state.vector_store = vector_store
            st.session_state.file_name = file_key
            st.session_state.messages = []
        st.success("✅ PDF ready! Ask me anything about it.")

elif not api_key:
    st.warning("👈 Please enter your Gemini API key in the sidebar.")
elif not use_sample and not uploaded_file:
    st.info("👈 Upload a PDF or check 'Use sample PDF' to get started.")

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            st.markdown(f"""<div class='source-box'>📌 <b>Source chunks used:</b> {msg['sources']}</div>""", unsafe_allow_html=True)

if not st.session_state.messages and api_key and (use_sample or uploaded_file):
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 2rem'>
        <h3>👋 Ready to chat!</h3>
        <p>Ask anything about your PDF below</p>
    </div>
    """, unsafe_allow_html=True)

if prompt := st.chat_input("Ask something about your PDF..."):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not use_sample and not uploaded_file:
        st.warning("Please upload a PDF or use the sample.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources = get_answer(
                    prompt,
                    st.session_state.vector_store,
                    st.session_state.messages,
                    api_key
                )
            st.write(answer)
            if sources:
                st.markdown(f"""<div class='source-box'>📌 <b>Source chunks used:</b> {sources}</div>""", unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

# --- Footer ---
st.markdown("<div class='footer'>Built with ❤️ using RAG + Google Gemini + FAISS</div>", unsafe_allow_html=True)