import streamlit as st
from pdf_processor import process_pdf, get_answer

# --- Page Config ---
st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="📄",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .stats-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin: 5px;
    }
    .footer {
        text-align: center;
        color: gray;
        font-size: 12px;
        padding-top: 2rem;
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
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        st.info(f"📊 Size: {round(uploaded_file.size/1024, 1)} KB")

    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("- *Summarize this document*")
    st.markdown("- *What are the key points?*")
    st.markdown("- *Who is mentioned in this?*")

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Process PDF ---
if uploaded_file and api_key:
    if "vector_store" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        with st.spinner("🔍 Reading and indexing your PDF..."):
            vector_store = process_pdf(uploaded_file, api_key)
            st.session_state.vector_store = vector_store
            st.session_state.file_name = uploaded_file.name
            st.session_state.messages = []
        st.success("✅ PDF ready! Ask me anything about it.")

elif not api_key:
    st.warning("👈 Please enter your Gemini API key in the sidebar to get started.")
elif not uploaded_file:
    st.info("👈 Please upload a PDF file in the sidebar to get started.")

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Empty state
if not st.session_state.messages and uploaded_file and api_key:
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 2rem'>
        <h3>👋 Ready to chat!</h3>
        <p>Ask anything about your PDF below</p>
    </div>
    """, unsafe_allow_html=True)

# Input
if prompt := st.chat_input("Ask something about your PDF..."):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not uploaded_file:
        st.warning("Please upload a PDF first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_answer(
                    prompt,
                    st.session_state.vector_store,
                    st.session_state.messages,
                    api_key
                )
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# --- Footer ---
st.markdown("""
<div class='footer'>
    Built with ❤️ using RAG + Google Gemini + FAISS
</div>
""", unsafe_allow_html=True)