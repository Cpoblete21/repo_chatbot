"""Theme configuration and common styles for the CMDB Dashboard."""

THEME = {
    'colors': {
        'primary': "#2C5030",
        'secondary': "#22C736",
        'accent': '#E74C3C',
        'background': "#F9F7F7",
        'card': "rgba(200, 200, 200, 0.11)",
        'text': "#050505",
        'border': '#E2E8F0'
    },
    'typography': {
        'fontFamily': 'Inter, sans-serif',
        'sizes': {
            'h1': '2.5rem',
            'h2': '2rem',
            'h3': '1.75rem',
            'body': '1rem'
        }
    },
    'spacing': {
        'xs': '0.5rem',
        'sm': '1rem',
        'md': '1.5rem',
        'lg': '2rem',
        'xl': '3rem'
    }
}

# Common style configurations
CARD_STYLE = {
    'padding': THEME['spacing']['lg'],
    'backgroundColor': THEME['colors']['card'],
    'borderRadius': '12px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}

DROPDOWN_STYLE = {
    'border': f'1px solid {THEME["colors"]["border"]}',
    'borderRadius': '8px',
    'marginBottom': THEME['spacing']['md']
}

BUTTON_STYLE = {
    'backgroundColor': THEME['colors']['secondary'],
    'color': 'white',
    'padding': f'{THEME["spacing"]["xs"]} {THEME["spacing"]["md"]}',
    'border': 'none',
    'borderRadius': '8px',
    'fontWeight': '500',
    'cursor': 'pointer',
    'transition': 'background-color 0.2s'
}

# Graph theme configuration
GRAPH_THEME = {
    'layout': {
        'plot_bgcolor': THEME['colors']['card'],
        'paper_bgcolor': THEME['colors']['card'],
        'font': {
            'family': THEME['typography']['fontFamily'],
            'color': THEME['colors']['text']
        },
        'title': {
            'font': {
                'family': THEME['typography']['fontFamily'],
                'size': 20,
                'weight': 600
            }
        },
        'margin': {'t': 40, 'r': 20, 'l': 20, 'b': 40}
    }
}

# Container styles
CONTAINER_STYLE = {
    'maxWidth': '1200px',
    'margin': '0 auto',
    'padding': f'0 {THEME["spacing"]["sm"]}'
}

# Header styles
HEADER_STYLE = {
    'background': f'linear-gradient(135deg, {THEME["colors"]["primary"]} 0%, {THEME["colors"]["secondary"]} 100%)',
    'marginBottom': THEME['spacing']['lg'],
    'padding': THEME['spacing']['lg']
}

# Grid styles
GRID_STYLE = {
    'display': 'grid',
    'gridTemplateColumns': 'repeat(2, 1fr)',
    'gap': THEME['spacing']['md']
}

# Text input styles
TEXTAREA_STYLE = {
    'width': '100%',
    'height': '120px',
    'padding': THEME['spacing']['sm'],
    'borderRadius': '8px',
    'border': f'1px solid {THEME["colors"]["border"]}',
    'marginBottom': THEME['spacing']['sm'],
    'fontFamily': THEME['typography']['fontFamily'],
    'resize': 'vertical'
}
