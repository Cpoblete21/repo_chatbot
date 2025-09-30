import requests
from tiktoken import encoding_for_model
import tiktoken
from .db_utils import connect_db, insert_repo_chunk_embedding, query_similar_chunks
from .git_utils import prepare_text_for_embedding

API_KEY = "REPLACE WITH API KEY"
MODEL_ID = "REPLACE WITH EMBEDDING MODEL"
BASE_URL = "COMPANY Or PERSONAL BASE URL"
CHAT_MODEL= "DESIRED CHAT MODEL"

#CHUNK_SIZE = 1000  # approximate number of characters per chunk

#def chunk_text(text, chunk_size=CHUNK_SIZE):
    #"""
    #Split text into chunks of roughly chunk_size characters.
    #"""
    #return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# -------------------------------
# Token-based chunking
# -------------------------------
MAX_TOKENS = 8000  # leave some buffer from the model max
RETRY_LIMIT = 3
RETRY_DELAY = 2  # seconds
ENCODER= tiktoken.get_encoding("cl100k_base")

def chunk_text_by_tokens(text, model_id=MODEL_ID, max_tokens=MAX_TOKENS):
    """
    Split text into chunks based on tokens, respecting max_tokens.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    
    
    tokens = ENCODER.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        chunks.append(ENCODER.decode(chunk_tokens))
    return chunks



def get_embedding(text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "input": text,
        #"messages": [
            #{"role": "user", "content": text}
        #]
    }
    response = requests.post(f"{BASE_URL}/embeddings", json=payload, headers=headers)
    if response.status_code == 200:
        # adjust this depending on their API response format
        return response.json()["data"][0]["embedding"]
    else:
        raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")


def test_gpt_connection():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": CHAT_MODEL,  # your GPT model, e.g., "gpt-4o-mini"
        "messages": [
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        "max_tokens": 50
    }
    
    response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    
    if response.status_code == 200:
        output = response.json()
        print(":D MODEL connection successful!")
        print("Response:", output["choices"][0]["message"]["content"])
    else:
        print("X MODEL connection failed!")
        print(response.status_code, response.text)

# Run the test
#test_gpt_connection()

def embed_large_text(repo_info):
    """
    Prepares repo text, chunks it, and returns embeddings with metadata.
    """
    full_text = prepare_text_for_embedding(repo_info)
    chunks = chunk_text_by_tokens(full_text)
    
    embeddings_data = []
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        embeddings_data.append({
            "repo_name": repo_info["repo_name"],
            "chunk_index": i,
            "text_chunk": chunk,
            "embedding": emb
        })
    
    return embeddings_data



# -------------------------------
# Store chunks in DB
# -------------------------------
def store_chunks_in_db(repo_info, embeddings_data):
    conn, cur = connect_db()
    for chunk in embeddings_data:
        insert_repo_chunk_embedding(
            cur=cur,
            repo_name=chunk["repo_name"],
            commit_hash=repo_info.get("commit_hash",""),
            commit_messages=repo_info.get("commit_messages",""),
            chunk_index=chunk["chunk_index"],
            file_path=chunk.get("file_path",""),
            text_chunk=chunk["text_chunk"],
            embedding=chunk["embedding"]
        )
    conn.commit()
    cur.close()
    conn.close()

# -------------------------------
# Question answering
# -------------------------------
def answer_question(question, top_k=5):
    """Answer questions using context from similar chunks."""
    conn, cur = connect_db()
    q_emb = get_embedding(question)
    chunks = query_similar_chunks(cur, q_emb, top_k=top_k)
    context = "\n\n".join([c["text_chunk"] for c in chunks])

    prompt = f"""
    Use the following repo context to answer the question:

    {context}

    Question: {question}
    """

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": CHAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
    )
    result = response.json()
    answer = result["choices"][0]["message"]["content"].strip()
    cur.close()
    conn.close()
    return answer



# Testing conectividad 
try:
    emb = get_embedding("Hello world")
    print("✅ AI connection successful! Embedding length:", len(emb))
except Exception as e:
    print(e)
