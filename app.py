import streamlit as st
from pdf_processor import process_pdf, get_answer

# --- Page Config ---
st.set_page_config(page_title="Chat with PDF", page_icon="📄", layout="centered")

st.title("📄 Chat with your PDF")
st.caption("Upload any PDF and ask questions about it — powered by RAG + Gemini")

# --- Sidebar: API Key + Upload ---
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} uploaded!")

# --- Process PDF when uploaded ---
if uploaded_file and api_key:
    if "vector_store" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        with st.spinner("Reading and indexing your PDF..."):
            vector_store = process_pdf(uploaded_file, api_key)
            st.session_state.vector_store = vector_store
            st.session_state.file_name = uploaded_file.name
            st.session_state.messages = []
        st.success("✅ PDF indexed! Start asking questions below.")

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input box
if prompt := st.chat_input("Ask something about your PDF..."):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not uploaded_file:
        st.warning("Please upload a PDF first.")
    else:
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get AI answer
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