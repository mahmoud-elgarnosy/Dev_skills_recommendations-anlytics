from dash import dcc, html
import app_utils


def create_layout():
    """
    Create the main layout of the job category predictor application.

    Returns:
        html.Div: The main layout containing UI components and callbacks.
    """
    # Get the categories and skills from app_utils
    categories_skills = app_utils.get_categories_skills()

    # Create the main layout using Dash HTML components
    app_layout = html.Div([
        html.H1("Anticipate my job and simulate more skills", style={'textAlign': 'center'}),

        # Main container for the page
        html.Div(
            id="main-container",
            children=[
                # Control board on the left half
                html.Div(
                    id="control-board",
                    children=[
                        app_utils.create_min_max_skills_header(),
                        *[
                            html.Div([
                                html.Div(html.H3(category, style={'textAlign': 'center'}), className='column-left'),
                                html.Div(app_utils.get_checklist(category, skills), className='column-right'),
                            ], className='row', style={'width': '100%', 'margin': 'auto', 'paddingBottom': '10px',
                                                       'borderBottom': '1px solid #ccc'})
                            for category, skills in categories_skills.items()
                        ],
                    ],
                    style={'width': '60%', 'float': 'left'}
                ),

                # Chart section on the right half
                html.Div([
                    app_utils.create_toggle_switch(),
                    html.Div(id="selected-skills-output", className='pretty_container'),
                    html.Div(id="mode-content", children=[
                        app_utils.create_probability_chart(),
                        dcc.RadioItems(id="job-radio"),
                        html.Div(id="loading-output"),
                        html.Div(id="simulated-skills-output"),
                        html.Div(id='current-target-job')
                    ])
                    # create_probability_chart(),

                ], style={'width': '45%', 'float': 'right'}),
            ],
            style={'width': '100%', 'display': 'flex', 'overflow': 'hidden'}
        )
    ])

    return app_layout
