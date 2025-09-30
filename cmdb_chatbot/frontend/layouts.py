"""Page layouts for the CMDB Dashboard."""

from dash import html, dcc
from frontend.components import (
    create_header,
    create_container,
    create_analytics_section,
    create_chatbot_section,
    create_dropdown,
    create_textarea
)

def create_analytics_tab(repo_options):
    """Create the Repository Analytics tab layout."""
    analytics_dropdown = create_dropdown(
        id="analytics-repo-dropdown",
        options=repo_options,
        placeholder="Select repositories...",
        multi=True,
        searchable=True,
        clearable=True
    )

    graphs = [
        dcc.Graph(id="commits-dist"),
        dcc.Graph(id="files-dist"),
        dcc.Graph(id="commits-box"),
        dcc.Graph(id="commits-violin"),
        dcc.Graph(id="lang-heatmap"),
        dcc.Graph(id="metrics-corr")
    ]

    return html.Div([
        create_analytics_section(
            title="Repository Metrics",
            dropdowns=[analytics_dropdown],
            graphs=graphs
        )
    ])

def create_chatbot_tab(repo_options):
    """Create the Chatbot QA tab layout."""
    repo_dropdown = create_dropdown(
        id="repo-dropdown",
        options=repo_options,
        placeholder="Select a repo...",
        multi=True,
        searchable=True,
        clearable=True
    )

    question_input = create_textarea(
        id="question-input",
        placeholder="Type your question..."
    )

    ask_button = html.Button("Ask", id="ask-btn")
    

    return create_chatbot_section(
        title="Ask about your repos",
        repo_dropdown=repo_dropdown,
        question_input=question_input,
        ask_button=ask_button,
        
    )



def create_main_layout(repo_options):
    """Create the main application layout."""
    return html.Div([
        create_header("CMDB Repo Dashboard"),
        create_container([
            dcc.Tabs([
                dcc.Tab(
                    label='Repository Analytics',
                    children=[create_analytics_tab(repo_options)]
                ),
                dcc.Tab(
                    label='Chatbot QA',
                    children=[create_chatbot_tab(repo_options)]
                )
            ])
        ])
    ])


