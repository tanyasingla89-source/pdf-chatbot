import faiss
import numpy as np
import PyPDF2
from google import genai

def configure_gemini(api_key):
    client = genai.Client(api_key=api_key)
    return client

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text_by_page = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            text_by_page.append((i + 1, text))  # (page_number, text)
    return text_by_page

def split_into_chunks(text_by_page, chunk_size=500):
    chunks = []
    for page_num, text in text_by_page:
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append({
                "text": chunk,
                "page": page_num
            })
    return chunks

def get_embeddings(client, texts):
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        embeddings.append(result.embeddings[0].values)
    return np.array(embeddings, dtype='float32')

def process_pdf(uploaded_file, api_key):
    client = configure_gemini(api_key)
    text_by_page = extract_text_from_pdf(uploaded_file)
    chunks = split_into_chunks(text_by_page)
    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(client, texts)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)
    return {
        "index": index,
        "chunks": chunks,
        "client": client
    }

def get_answer(question, vector_store, chat_history, api_key):
    client = vector_store["client"]

    # Embed the question
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )
    question_embedding = np.array([result.embeddings[0].values], dtype='float32')

    # Find top 3 relevant chunks
    _, indices = vector_store["index"].search(question_embedding, k=3)
    relevant_chunks = [vector_store["chunks"][i] for i in indices[0]]

    # Build context with page numbers
    context = ""
    pages_used = []
    for chunk in relevant_chunks:
        context += f"\n[Page {chunk['page']}]: {chunk['text']}\n"
        if chunk['page'] not in pages_used:
            pages_used.append(chunk['page'])

    # Format source citation
    pages_str = ", ".join([f"Page {p}" for p in sorted(pages_used)])

    # Generate answer
    prompt = f"""You are a helpful assistant. Answer the question based on the context below.
If the answer is not in the context, say "I couldn't find that in the document."

Context:
{context}

Question: {question}

Answer:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text, pages_str