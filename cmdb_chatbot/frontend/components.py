"""Reusable components for the CMDB Dashboard."""

from dash import html, dcc 
from frontend.assets.theme import (
    THEME,
    CARD_STYLE,
    DROPDOWN_STYLE,
    BUTTON_STYLE,
    TEXTAREA_STYLE,
    CONTAINER_STYLE,
    HEADER_STYLE,
    GRID_STYLE
)

def create_header(title):
    """Create a header component with gradient background."""
    return html.Div([
        html.H1(title, style={'color': 'white', 'margin': 0})
    ], style=HEADER_STYLE)

def create_container(children):
    """Create a centered container with max-width."""
    return html.Div(children, style=CONTAINER_STYLE)

def create_card(children, additional_style=None):
    """Create a card component with shadow and rounded corners."""
    style = CARD_STYLE.copy()
    if additional_style:
        style.update(additional_style)
    return html.Div(children, className='card fade-in', style=style)

def create_dropdown(id, options, **kwargs):
    """Create a styled dropdown component."""
    return dcc.Dropdown(
        id=id,
        options=options,
        style=DROPDOWN_STYLE,
        **kwargs
    )

def create_button(id, text, additional_style=None):
    """Create a styled button component."""
    style = BUTTON_STYLE.copy()
    if additional_style:
        style.update(additional_style)
    return html.Button(text, id=id, className='button', style=style)

def create_textarea(id, placeholder="", additional_style=None):
    """Create a styled textarea component."""
    style = TEXTAREA_STYLE.copy()
    if additional_style:
        style.update(additional_style)
    return dcc.Textarea(
        id=id,
        placeholder=placeholder,
        style=style
    )

def create_form_group(label, component):
    """Create a form group with label and component."""
    return html.Div([
        html.Label(label, className='form-label'),
        component
    ], className='form-group')

def create_grid(children):
    """Create a responsive grid layout."""
    return html.Div(children, style=GRID_STYLE)

def create_graph_container(graph):
    """Create a container for graph components."""
    return html.Div(graph, className='graph-container')

def create_analytics_section(title, dropdowns=None, graphs=None):
    """Create a section for analytics with title, dropdowns, and graphs."""
    children = []
    if title:
        children.append(html.H3(title))
    
    if dropdowns:
        children.append(html.Div(dropdowns, className='form-group'))
    
    if graphs:
        children.append(create_grid(
            [create_graph_container(graph) for graph in graphs]
        ))
    
    return create_card(children)

#def create_chatbot_section(title, repo_dropdown, question_input, ask_button):
    """Create the chatbot section with all its components."""
    return create_card([
        html.H3(title),
        create_form_group("Select a repository:", repo_dropdown),
        create_form_group("Ask a question:", question_input),
        create_button(ask_button.id, "Ask"),
        dcc.Markdown( id="answer-output", className='fade-in')
    ])
def create_chatbot_section(title, repo_dropdown, question_input, ask_button):
    """Create the chatbot section with all its components."""
    return html.Div([
        html.H3(title),
        # Two-column container
        html.Div([
            # Left column
            html.Div([
                create_form_group("Select a repository:", repo_dropdown),
                create_form_group("Ask a question:", question_input),
                create_button(ask_button.id, "Ask"),
            ], className='chat-input-column'),
            
            # Right column
            html.Div([
                dcc.Markdown(id="answer-output", className='answer-output')
            ], className='chat-output-column')
        ], className='chat-grid')
    ], className='chat-container')
