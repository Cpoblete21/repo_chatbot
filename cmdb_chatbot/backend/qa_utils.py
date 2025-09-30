from .db_utils import connect_db, query_similar_chunks, get_all_repo_names ,TABLE
from .ai_utils import get_embedding, API_KEY, BASE_URL, CHAT_MODEL
import re
import requests
import json
from difflib import get_close_matches 
from .nlp_utils import extract_intent as nlp_extract_intent

def extract_intent(question):
    return nlp_extract_intent(question)

# -------------------------------
# Repo name extraction with fallback
# -------------------------------
def extract_repo_name(question, known_repos=None):
    if known_repos is None:
        known_repos = get_all_repo_names()  # Fetch from DB
    
    match = re.search(r"in repo (\S+)", question.lower())
    if match:
        repo_candidate = match.group(1)
        if repo_candidate in known_repos:
            return repo_candidate

    for repo in known_repos:
        if repo.lower() in question.lower():
            return repo

    closest = get_close_matches(question, known_repos, n=1, cutoff=0.5)
    if closest:
        return closest[0]

    return known_repos[0] if known_repos else "default_repo_name"

# -------------------------------
# Structured question handler
# -------------------------------
def handle_structured_question(question, cur, repo_name):
    # First try to extract intent
    intent = extract_intent(question)
    

    # Use intent if available, otherwise fallback to keyword matching
    if intent == 'commit_count':
        cur.execute(f"SELECT total_commits FROM {TABLE} WHERE repo_name=%s", (repo_name,))
        row = cur.fetchone()
        if row:
            return f"Total commits: {row[0]}"
        return "No commit information found"

    # Most active contributor
    elif intent=='most_active':
        cur.execute(f"""
        WITH contributor_stats AS (
            SELECT 
                most_active_contributor,
                total_commits,
                (SELECT jsonb_array_length(contributors)) as contributor_count
            FROM {TABLE}
            WHERE repo_name = %s
        )
        SELECT most_active_contributor, contributor_count, total_commits
        FROM contributor_stats;
    """, (repo_name,))
        row = cur.fetchone()
        if row and row[0]:
            email = row[0]
            commit_count = row[1] or 0  # In case it's NULL
            total_commits = row[2]
            percentage = (commit_count / total_commits * 100) if total_commits > 0 else 0
            return f"Most active contributor: {email} with {commit_count} commits ({percentage:.1f}% of total commits)"

    # Languages and files count
    elif intent =='languages':
        cur.execute(f"""
        SELECT languages, files_count 
        FROM {TABLE} 
        WHERE repo_name = %s
    """, (repo_name,))
        row = cur.fetchone()
        if row:
            languages = row[0]  # This is JSONB
            files_count = row[1]
            lang_list = "\n".join([f"- {lang}: {count} files" for lang, count in languages.items()])
            return f"Repository contains {files_count} files:\n\nLanguage breakdown:\n{lang_list}"
        return "No language or file information found"

    # Version information
    elif intent =='version':
        cur.execute(f"""
        SELECT tags, branches 
        FROM {TABLE} 
        WHERE repo_name = %s
    """, (repo_name,))
        row = cur.fetchone()
        if row:
            tags, branches = row[0], row[1]
            response_parts = []
        
            if tags and len(tags) > 0:
                response_parts.append(f"Version tags for {repo_name}:")
                for tag in tags:
                    response_parts.append(f"- {tag}")
            else:
                response_parts.append("No version tags found")
                
            if branches and len(branches) > 0:
                response_parts.append("\nActive branches:")
                for branch in branches:
                    response_parts.append(f"- {branch}")
                
            return "\n".join(response_parts)
        return "No version information found"

    # Dependencies check using languages
    elif intent =='dependencies':
        cur.execute(f"""
        SELECT languages 
        FROM {TABLE} 
        WHERE repo_name = %s
    """, (repo_name,))
        row = cur.fetchone()
        if row and row[0]:
            languages = row[0]
            response = ["Likely dependencies based on project languages:"]
            
            if "java" in languages:
                response.append("Java dependencies (check pom.xml or build.gradle):")
                response.append("- Spring Framework")
                response.append("- Maven/Gradle build system")
                
            if "python" in languages or "py" in languages:
                response.append("\nPython dependencies (check requirements.txt or setup.py):")
                response.append("- Python packages")
                response.append("- pip package manager")
                
            if "javascript" in languages or "js" in languages:
                response.append("\nJavaScript dependencies (check package.json):")
                response.append("- npm packages")
                response.append("- Node.js runtime")
                
            return "\n".join(response)
        return "No language information found"

    # Contribution trend
    elif intent == 'contribution_trend':
        cur.execute(f"""
        SELECT 
            first_commit_date,
            last_commit_date,
            total_commits
        FROM {TABLE}
        WHERE repo_name = %s
    """, (repo_name,))
        row = cur.fetchone()
        if row:
            first_date = row[0]
            last_date = row[1]
            total = row[2]
            days_diff = (last_date - first_date).days
            avg_commits = total / days_diff if days_diff > 0 else 0
        
            return f"""Contribution trend for {repo_name}:
    - First commit: {first_date.strftime('%Y-%m-%d')}
    - Last commit: {last_date.strftime('%Y-%m-%d')}
    - Total commits: {total}
    - Repository age: {days_diff} days
    - Average commits per day: {avg_commits:.2f}"""
        return "No contribution data found"

    # Last commit message
    elif  intent == 'last_commit':
        cur.execute(f"SELECT commit_messages FROM {TABLE} WHERE repo_name=%s", (repo_name,))
        row = cur.fetchone()
        if row and row[0]:
            last_commit = row[0][-1] if isinstance(row[0], list) else row[0]
            return f"Last commit message: {last_commit}"
        return "No commit messages found"

    return "Question not understood"

# -------------------------------
# Hybrid QA function
# -------------------------------
def get_repo_context(cur, repo_name):
    """Get comprehensive repository context for AI processing"""
    cur.execute(f"""
        SELECT 
            total_commits,
            languages,
            files_count,
            first_commit_date,
            last_commit_date,
            most_active_contributor,
            branches,
            tags
        FROM {TABLE}
        WHERE repo_name = %s
    """, (repo_name,))
    row = cur.fetchone()
    if row:
        return {
            "name": repo_name,
            "total_commits": row[0],
            "languages": row[1],
            "files_count": row[2],
            "first_commit": row[3].strftime('%Y-%m-%d') if row[3] else None,
            "last_commit": row[4].strftime('%Y-%m-%d') if row[4] else None,
            "top_contributor": row[5],
            "branches": row[6],
            "tags": row[7]
        }
    return None

def calculate_confidence_score(context_chunks, question_type):
    """
    Calculate a confidence score based on context quality and relevance.
    """
    if not context_chunks:
        return 0.0
    
    # Base score from highest relevance chunk
    base_score = max(chunk.get('final_score', 0) for chunk in context_chunks)
    
    # Adjust based on context type coverage
    has_code = any(chunk['metadata']['is_code'] for chunk in context_chunks)
    has_docs = any(chunk['metadata']['is_doc'] for chunk in context_chunks)
    context_coverage = 0.2 * (has_code + has_docs)
    
    # Adjust based on number of relevant chunks
    chunk_count_factor = min(len(context_chunks) / 5, 1.0) * 0.2
    
    # Adjust based on question type
    type_multiplier = {
        'code': 1.2 if has_code else 0.8,
        'doc': 1.2 if has_docs else 0.8,
        'general': 1.0
    }.get(question_type, 1.0)
    
    final_score = (base_score * 0.6 + context_coverage + chunk_count_factor) * type_multiplier
    return min(final_score, 1.0)

def validate_response(answer, confidence_score,repo_name):
    """
    Validate and potentially enhance the response based on confidence.
    """
    #  confidence indicator
    confidence_level = "High" if confidence_score >= 0.8 else "Medium" if confidence_score >= 0.5 else "Low"
    
    # Format answer with confidence header
    formatted_answer = f"""
        
        # Repository: {repo_name}
       ## Confidence Level: **{confidence_level}** ({confidence_score:.2f})

        {answer}

        """
    
    # Add caveats for low confidence
    if confidence_score < 0.5:
        formatted_answer += "\n\n> **Note:** This answer is based on limited information and should be verified."
    
    return formatted_answer

def process_with_ai(question, context_chunks, repo_data,repo_name):
    """
    Process a question using AI with enhanced context handling and answer synthesis.
    
    Args:
        question: The user's question
        context_chunks: List of context chunks with metadata and relevance scores
        repo_data: Repository metadata
    Returns:
        Validated and formatted response with confidence scoring
    """
    system_message = """You are a concise repository assistant. Provide brief, focused answers about code repositories.

    Guidelines for responses:
    1. Keep answers short and direct - maximum 2-3 sentences when possible
    2. Only include technical details if specifically asked
    3. Use simple language, avoid unnecessary jargon
    4. Skip file citations unless explicitly requested
    5. Show confidence level only if below 0.7
    6. Show the output in Markdown format
    7. When the question relates a key value answer show the answers in side by side table 
    8.  Use this exact table format for all metrics:
            | Metric | Value |
            |--------|-------|
            | Key 1 | Value 1 |
            | Key 2 | Value 2 |

    """
    


    # Format repository context with additional insights
    activity_level = "high" if repo_data['total_commits'] > 1000 else "medium" if repo_data['total_commits'] > 100 else "low"
    primary_languages = sorted(repo_data['languages'].items(), key=lambda x: x[1], reverse=True)[:3]
    
    repo_context = f"""
    Repository Overview:
    - Name: {repo_data['name']}
    - Activity Level: {activity_level} ({repo_data['total_commits']} total commits)
    - Primary Languages: {', '.join(f"{lang} ({count} files)" for lang, count in primary_languages)}
    - Project Scale: {repo_data['files_count']} total files
    - Development Timeline: {repo_data['first_commit']} to {repo_data['last_commit']}
    - Main Contributor: {repo_data['top_contributor']}
    - Active Branches: {', '.join(repo_data['branches']) if repo_data['branches'] else 'N/A'}
    - Release Tags: {', '.join(repo_data['tags']) if repo_data['tags'] else 'N/A'}
    """

    # Process and organize context chunks
    organized_context = []
    code_contexts = []
    doc_contexts = []
    
    for chunk in context_chunks:
        context_entry = f"""
        Source: {chunk['file_path']} (Relevance: {chunk['final_score']:.2f})
        Content: {chunk['text_chunk']}
        """
        if chunk['metadata']['is_code']:
            code_contexts.append(context_entry)
        elif chunk['metadata']['is_doc']:
            doc_contexts.append(context_entry)
        else:
            organized_context.append(context_entry)

    # Construct the enhanced prompt
    prompt = f"""Based on the following repository information and context, please provide a comprehensive answer to the question.

{repo_context}

Relevant Documentation:
{chr(10).join(doc_contexts[:2]) if doc_contexts else "No relevant documentation found."}

Relevant Code:
{chr(10).join(code_contexts[:2]) if code_contexts else "No relevant code snippets found."}

Additional Context:
{chr(10).join(organized_context[:2]) if organized_context else "No additional context available."}

Question: {question}

Please provide a detailed answer that:
1. Directly addresses the question using the most relevant information
2. Cites specific files, code, or documentation when applicable
3. Includes technical details and metrics that support your response
4. Clearly indicates confidence levels for different parts of your answer
5. Synthesizes information from multiple sources when available
"""

    # Make the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3  # Lower temperature for more focused responses
    }
    
    response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
    
    if response.status_code != 200:
        return "I apologize, but I encountered an error while processing your question. Please try again."
    
    result = response.json()
    raw_answer = result["choices"][0]["message"]["content"].strip()
    
    # Determine question type based on context and question
    question_type = 'code' if any(word in question.lower() for word in ['code', 'implementation', 'function', 'class']) else \
                   'doc' if any(word in question.lower() for word in ['documentation', 'readme', 'guide', 'explain']) else \
                   'general'
    
    # Calculate confidence score
    confidence_score = calculate_confidence_score(context_chunks, question_type)
    
    # Validate and format the response
    final_answer = validate_response(raw_answer, confidence_score,repo_name)
    
    return final_answer

def answer_hybrid(question, top_k=5, repo_name=None):
    conn, cur = connect_db()

    try:
        # Get known repos from DB
        cur.execute(f"SELECT repo_name FROM {TABLE};")
        known_repos = [row[0] for row in cur.fetchall()]

        # Extract repo from question
        repo_name = repo_name or extract_repo_name(question, known_repos)

        # Try structured queries first
        structured_answer = handle_structured_question(question, cur, repo_name=repo_name)
        
        # Get context and repo data for AI processing
        repo_data = get_repo_context(cur, repo_name)
        q_emb = get_embedding(question)
        context_chunks = query_similar_chunks(cur, q_emb, top_k=top_k)

        # If we have a structured answer, add it as a high-confidence context
        if structured_answer:
            context_chunks.insert(0, {
                "text_chunk": structured_answer,
                "file_path": "structured_query_result",
                "final_score": 1.0,
                "metadata": {
                    "is_code": False,
                    "is_doc": True,
                    "file_type": "txt"
                }
            })
        
        # Process with AI using enhanced context
        return process_with_ai(question, context_chunks, repo_data,repo_name)

    finally:
        cur.close()
        conn.close()
