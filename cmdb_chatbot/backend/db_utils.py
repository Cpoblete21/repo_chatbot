import re
import psycopg2
from psycopg2.extras import Json
from .db_config import DB_HOST, DB_NAME, DB_PSSWRD, DB_PORT, DB_USER
from .db_config import SCHEMA


TABLE = f'{SCHEMA}.reposvectorial'

# -------------------------------
# Database helper functions
# -------------------------------
def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PSSWRD,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("✅ Database connection successful!")
        return conn, cur
    except Exception as e:
        print("❌ Failed to connect to database:", e)
        raise e




def ensure_chunks_table_exists(cur):
        # First create the schema
    cur.execute(f"""
        CREATE SCHEMA IF NOT EXISTS general;
    """)

        # Create vector extension
    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE}_chunks (
            id SERIAL PRIMARY KEY,
            repo_name TEXT, 
            commit_hash TEXT,
            commit_messages TEXT,
            chunk_index INT,
            file_path TEXT,
            text_chunk TEXT, 
            embedding vector(3072)
        );
    """)





def ensure_table_exists(cur):
    # First create the schema
    cur.execute(f"""
        CREATE SCHEMA IF NOT EXISTS general;
    """)

        # Create vector extension
    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)
    
    # Then create the table
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            id SERIAL PRIMARY KEY,
            repo_name TEXT NOT NULL,
            total_commits INT,
            branches TEXT[],
            tags TEXT[],
            contributors JSONB,
            most_active_contributor JSONB,
            first_commit_date TIMESTAMP,
            last_commit_date TIMESTAMP,
            languages JSONB,
            files_count INT,
            commit_messages JSONB,
            embedding vector(3072)
        );
    """)


def insert_repo_metadata(cur, repo_info, embedding):
    """Insert a single repo's metadata into the table"""
    cur.execute(f"""
        INSERT INTO {TABLE} 
        (repo_name, total_commits, branches, tags, contributors, 
         most_active_contributor, first_commit_date, last_commit_date, languages, files_count, commit_messages, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        repo_info["repo_name"],
        repo_info["total_commits"],
        repo_info["branches"],
        repo_info["tags"],
        Json(repo_info["contributors"]),
        Json(repo_info["most_active_contributor"]),
        repo_info["first_commit_date"],
        repo_info["last_commit_date"],
        Json(repo_info["languages"]),
        repo_info["files_count"],
        Json(repo_info["commit_messages"]),
        embedding
    ))

def insert_repo_chunk_embedding(cur, repo_name, commit_hash, commit_messages,chunk_index ,file_path, text_chunk, embedding):
    cur.execute(f"""
        INSERT INTO {TABLE}_chunks (
            repo_name, commit_hash, commit_messages, chunk_index ,file_path, text_chunk, embedding
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        repo_name,
        commit_hash,
        commit_messages,
        chunk_index,
        file_path,
        text_chunk,
        embedding  # ✅ this is now stored
    ))



def insert_repo_metadata_with_embedding(cur, repo_info, embedding):
    cur.execute(f"""
        INSERT INTO {TABLE} 
        (repo_name, total_commits, branches, tags, contributors, 
         most_active_contributor, first_commit_date, last_commit_date, languages, files_count, commit_messages, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        repo_info["repo_name"],
        repo_info["total_commits"],
        repo_info["branches"],
        repo_info["tags"],
        Json(repo_info["contributors"]),
        Json(repo_info["most_active_contributor"]),
        repo_info["first_commit_date"],
        repo_info["last_commit_date"],
        Json(repo_info["languages"]),
        repo_info["files_count"],
        Json(repo_info["commit_messages"]),
        embedding
    ))

# -------------------------------
# Query Functions
# -------------------------------

def query_similar_chunks(cur, query_embedding, top_k=5, similarity_threshold=0.8):
    """
    Query most similar chunks using enhanced ranking and filtering.
    
    Args:
        cur: Database cursor
        query_embedding: Vector embedding of the query
        top_k: Number of chunks to return
        similarity_threshold: Minimum similarity score (0-1) for chunks
    
    Returns:
        List of chunks with metadata and relevance scores
    """
    vector_literal = f"ARRAY{query_embedding}::vector"
    
    # Enhanced query with metadata and multiple ranking factors
    cur.execute(f"""
        WITH ranked_chunks AS (
            SELECT 
                c.id,
                c.repo_name,
                c.file_path,
                c.text_chunk,
                c.commit_hash,
                c.commit_messages,
                c.chunk_index,
                1 - (c.embedding <-> {vector_literal}) as similarity_score,
                
                -- Boost score for code files
                CASE 
                    WHEN c.file_path ~* '\.(py|js|java|cpp|h|cs|go|rs|sql)$' THEN 1.2
                    WHEN c.file_path ~* '\.(md|txt|rst|yaml|json|xml)$' THEN 1.1
                    ELSE 1.0
                END as file_type_boost,
                
                -- Boost score for more recent chunks
                CASE 
                    WHEN c.chunk_index >= 0 THEN 1 + (0.1 * (1.0 / (c.chunk_index + 1)))
                    ELSE 1.0
                END as recency_boost
                
            FROM {TABLE}_chunks c
            WHERE 1 - (c.embedding <-> {vector_literal}) > %s
        )
        SELECT 
            id,
            repo_name,
            file_path,
            text_chunk,
            commit_hash,
            commit_messages,
            chunk_index,
            similarity_score,
            similarity_score * file_type_boost * recency_boost as final_score
        FROM ranked_chunks
        ORDER BY final_score DESC
        LIMIT %s;
    """, (similarity_threshold, top_k))

    results = cur.fetchall()
    
    return [
        {
            "id": r[0],
            "repo_name": r[1],
            "file_path": r[2],
            "text_chunk": r[3],
            "commit_hash": r[4],
            "commit_messages": r[5],
            "chunk_index": r[6],
            "similarity_score": r[7],
            "final_score": r[8],
            "metadata": {
                "is_code": bool(re.search(r'\.(py|js|java|cpp|h|cs|go|rs|sql)$', r[2] or '')),
                "is_doc": bool(re.search(r'\.(md|txt|rst|yaml|json|xml)$', r[2] or '')),
                "file_type": r[2].split('.')[-1] if r[2] and '.' in r[2] else None
            }
        }
        for r in results
    ]


def get_all_commits(cur, repo_name):
    """
    Get all commit messages for a given repo.
    """
    cur.execute(f"""
        SELECT commit_messages
        FROM {TABLE}
        WHERE repo_name = %s
    """, (repo_name,))
    
    rows = cur.fetchall()
    # commit_messages is JSONB, so flatten if needed
    commits = []
    for row in rows:
        if isinstance(row[0], list):
            commits.extend(row[0])
        else:
            commits.append(row[0])
    return commits

def get_all_repo_names(cur):
    """
    Return a list of all repo names in your main table.
    """
    cur.execute(f"SELECT repo_name FROM {TABLE}")
    rows = cur.fetchall()
    return [r[0] for r in rows]



#def get_closest_repo_name(repo_name, all_repo_names, n=1, cutoff=0.6):
    """
    Return the closest matching repo name from the list.
    - n: number of matches to return (usually 1)
    - cutoff: similarity threshold (0 to 1)
    """
    matches = get_close_matches(repo_name, all_repo_names, n=n, cutoff=cutoff)
    if matches:
        return matches[0]
    return None
