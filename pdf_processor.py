import faiss
import numpy as np
import PyPDF2
from google import genai
from google.genai import types

def configure_gemini(api_key):
    client = genai.Client(api_key=api_key)
    return client

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def split_into_chunks(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
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
    text = extract_text_from_pdf(uploaded_file)
    chunks = split_into_chunks(text)
    embeddings = get_embeddings(client, chunks)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)
    return {"index": index, "chunks": chunks, "client": client}

def get_answer(question, vector_store, chat_history, api_key):
    client = vector_store["client"]
    result = client.models.embed_content(
       model="gemini-embedding-001",
        contents=question
    )
    question_embedding = np.array([result.embeddings[0].values], dtype='float32')
    _, indices = vector_store["index"].search(question_embedding, k=3)
    relevant_chunks = [vector_store["chunks"][i] for i in indices[0]]
    context = "\n\n".join(relevant_chunks)
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
    return response.text