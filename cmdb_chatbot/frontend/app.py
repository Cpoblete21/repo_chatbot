"""Main application file for the CMDB Dashboard."""

import dash
import sys
import os
from dash import Input, Output, State, html, dcc, callback_context
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.qa_utils import answer_hybrid
from backend.db_utils import get_all_repo_names, connect_db, ensure_chunks_table_exists, ensure_table_exists
from frontend.layouts import create_main_layout
from frontend.assets.theme import GRAPH_THEME
from frontend.dataviz import repo_metrics_distribution

# Initialize Dash 
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
        'rel': 'stylesheet',
    }
]

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    assets_folder='assets'
)
server = app.server

# Database setup
conn, cur = connect_db()
ensure_table_exists(cur)
ensure_chunks_table_exists(cur)

# Get repository options for dropdowns
repo_options = [{"label": name, "value": name} for name in get_all_repo_names(cur)]

# Close database connection
cur.close()
conn.close()

# Set the application layout
app.layout = html.Div([
    dcc.Store(id='answer-store', data=''),
    dcc.Store(id='stream-index', data=0),
    dcc.Interval(id='stream-interval', interval=50, disabled=True),
    create_main_layout(repo_options)
])

# Callbacks
@app.callback(
    [Output("commits-dist", "figure"),
     Output("files-dist", "figure"),
     Output("commits-box", "figure"),
     Output("commits-violin", "figure"),
     Output("lang-heatmap", "figure"),
     Output("metrics-corr", "figure")],
    Input("analytics-repo-dropdown", "value")
)
def update_analytics(selected_repos):
    """Update all analytics graphs based on selected repositories."""
    figures = repo_metrics_distribution(selected_repos) if selected_repos else repo_metrics_distribution()
    
    # Apply theme to all figures
    for figure in figures:
        if figure:
            figure.update_layout(**GRAPH_THEME['layout'])
    
    return figures


@app.callback(
    Output("answer-output", "children"),
    Input("ask-btn", "n_clicks"),
    State("question-input", "value"),
    State("repo-dropdown", "value")
)
def get_answer(n_clicks, question, selected_repos):
    """Get answer from the chatbot based on user input."""
    if not question or not selected_repos:
        return "Please select repositories and ask a question!", 0, True
    
    if isinstance(selected_repos, list):
        # Handle multiple repos
        answers = []
        for repo in selected_repos:
            answer = answer_hybrid(question, repo_name=repo)
            answers.append(f"For {repo}: {answer}")
        return "\n\n\n".join(answers), 0, False
    else:
        # Handle single repo
        answer = answer_hybrid(question, repo_name=selected_repos)
        return answer, 0, False


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=8050)

