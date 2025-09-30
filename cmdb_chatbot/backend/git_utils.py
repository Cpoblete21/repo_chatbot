import os
from git import Repo
from collections import Counter


# -------------------------------
# Git analysis functions
# -------------------------------
def analyze_repo(repo_path):
    repo = Repo(repo_path)
    commits = list(repo.iter_commits())
    
    repo_info = {
        "repo_name": os.path.basename(repo_path),
        "total_commits": len(commits),
        "branches": [h.name for h in repo.heads],
        "tags": [t.name for t in repo.tags],
        "contributors": list(set(commit.author.email for commit in commits)),
        "most_active_contributor": None,
        "first_commit_date": None,
        "last_commit_date": None,
        "languages": None,
        "files_count": 0,
        "commit_messages": [c.message.strip() for c in commits]
    }

    # Most active contributor
    author_counter = Counter(commit.author.email for commit in commits)
    if author_counter:
        repo_info["most_active_contributor"] = author_counter.most_common(1)[0][0]
    
    # Dates
    if commits:
        repo_info["first_commit_date"] = commits[-1].committed_datetime
        repo_info["last_commit_date"] = commits[0].committed_datetime
    
    # Files and languages
    file_extensions = Counter()
    for root, _, files in os.walk(repo_path):
        if ".git" in root:
            continue
        for f in files:
            repo_info["files_count"] += 1
            ext = os.path.splitext(f)[-1]
            if ext:
                file_extensions[ext] += 1
    repo_info["languages"] = dict(file_extensions.most_common(5))
    
    return repo_info


def prepare_text_for_embedding(repo_info, max_commits=50):
    """
    Prepare a rich textual summary of a repository for embedding.
    
    Args:
        repo_info (dict): Output from analyze_repo()
        max_commits (int): Number of recent commit messages to include

    Returns:
        str: A formatted text string ready for embeddings
    """
    # Top 5 file types with counts
    top_file_types = ', '.join(f"{ext}({count})" for ext, count in repo_info.get('languages', {}).items())
    
    # Contributors info
    total_contributors = len(repo_info.get('contributors', []))
    most_active = repo_info.get('most_active_contributor', 'N/A')
    
    # Commit info
    total_commits = repo_info.get('total_commits', 0)
    first_commit = repo_info.get('first_commit_date', 'N/A')
    last_commit = repo_info.get('last_commit_date', 'N/A')
    recent_commits = ' | '.join(repo_info.get('commit_messages', [])[-max_commits:])
    
    text = f"""
Repo: {repo_info.get('repo_name', 'N/A')}
Default branch: {repo_info.get('branches', ['N/A'])[0]}
Branches: {', '.join(repo_info.get('branches', []))}
Tags: {', '.join(repo_info.get('tags', []))}
Contributors ({total_contributors} total): {', '.join(repo_info.get('contributors', []))}
Most active contributor: {most_active}
Total commits: {total_commits}
First commit date: {first_commit}
Last commit date: {last_commit}
Top file types: {top_file_types}
Total files: {repo_info.get('files_count', 0)}
Recent commit messages: {recent_commits}
"""
    return text