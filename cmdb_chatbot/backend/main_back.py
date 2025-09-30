
import os
import numpy as np
import pandas as pd
from .git_utils import analyze_repo
from .db_utils import connect_db, ensure_table_exists, insert_repo_metadata, insert_repo_metadata_with_embedding,insert_repo_chunk_embedding, ensure_chunks_table_exists
from .ai_utils import embed_large_text, get_embedding, answer_question, store_chunks_in_db



def analyze_repos(base_folder):
    data = []
    conn, cur = connect_db()
    ensure_table_exists(cur)
    ensure_chunks_table_exists(cur)

    for name in os.listdir(base_folder):
        path = os.path.join(base_folder, name)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, ".git")):
            print(f"Analyzing {name}...")
            repo_info = analyze_repo(path)


            # Get chunked embeddings
            embeddings_data = embed_large_text(repo_info)


            embedding = np.mean([chunk["embedding"]for chunk in embeddings_data], axis=0)
            embedding_list = embedding.tolist()

            # Insert metadata & embeddings into Postgres
            insert_repo_metadata(cur, repo_info, embedding_list)
            for chunk_data in embeddings_data:
                insert_repo_chunk_embedding(
                    cur=cur,
                    repo_name=repo_info["repo_name"],  # ✅ use the repo_info, not chunk_data
                    commit_hash=repo_info.get("commit_hash",""),
                    commit_messages=repo_info.get("commit_messages",""),  # ✅ add commit message
                    chunk_index=chunk_data["chunk_index"],
                    file_path=chunk_data.get("file_path",""),
                    text_chunk=chunk_data["text_chunk"],
                    embedding=chunk_data["embedding"]
                    )
            
            data.append(repo_info)

    conn.commit()
    cur.close()
    conn.close()

    # Save CSV
    df = pd.DataFrame(data)
    df.to_csv("repos_metadata2.csv", index=False)
    print("✅ CSV exported as repos_metadata2.csv")
    return df


# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    folder = "/Users/cristobal.poblete/Desktop/codes/Repos"  # local repo 
    #folder= "/app/repos"        #docker path
    df = analyze_repos(folder)
    print(df)