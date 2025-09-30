# -------------------------------
# Intent extraction
# -------------------------------
def extract_intent(question):
    patterns = {
        'commit_count': [
            'how many commits', 'total commits', 'number of commits',
            'commit count', 'commits are there','tell me the commits', 'show me commit count'


        ],
        'most_active': [
            'most commits', 'top contributor', 'who contributed most',
            'most active', 'who made the most', 'who has contributed','biggest contributor',
            'primary contributor', 'main developer', 'who leads the development','who wrote the most amount of codes'
        ],
        'languages': [
            'what languages', 'programming languages', 'tech stack',
            'written in', 'developed in', 'coding languages','tell me about languages used',
            'show me the tech stack',
            'what technologies are used',
            'which programming languages',
            'development stack',
            'code languages',
            'what is it built with',
            'development technologies'
        ],
        'files': [ #not yet
            'what files', 'show files', 'list files',
            'what documents', 'file structure', 'repository contents'
        ],
        'version': [
            'version', 'release', 'tag', 'tagged version','what version is it',
            'tell me about versions',
            'show me releases',
            'latest version',
            'current release',
            'which version',
            'release history',
            'version information'
        ],
        'dependencies': [ #not yet
            'dependencies', 'packages', 'libraries', 'frameworks'
        ],
        'contribution_trend': [
            'contribution trend', 'commit trend', 'activity trend',
            'commit history', 'contribution history','how active is development',
            'show me development activity',
            'tell me about commit patterns',
            'development timeline',
            'project activity',
            'how often are commits made',
            'frequency of updates',
            'development progress'
        ],
        'last_commit': [
            'last commit', 'recent commit', 'latest commit',
            'most recent change'
        ]
    }
    
    question = question.lower()
    for intent, phrases in patterns.items():
        if any(phrase in question for phrase in phrases):
            return intent
    return None
