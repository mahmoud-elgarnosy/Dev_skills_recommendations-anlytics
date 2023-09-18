from dash import Dash, dcc, html, Input, Output
import dash
from src import anticipate_simulate_layout
from src import dashboard
from src import app_utils
from src import anticipate_simulate_callbacks

categories_skills = app_utils.get_categories_skills()

app = dash.Dash(__name__)
# Define the navigation links
nav_links = dcc.Link("Anticipate/Simulate", href="/predict-simulate", className="nav-link")
nav_links_simulate = dcc.Link("Dashboard", href="/dashboard", className="nav-link")
nav_links_dashboard = html.A('Portfolio', href='https://www.w3schools.com/', className="nav-link")
index_layout = html.Div(
    [
        html.Div(
            [
                html.H1("Stack Overflow 2023: Anticipate, Simulate, and Gain Insights for Your Career"),
                html.Div(
                    [
                        nav_links,
                        nav_links_simulate,
                        nav_links_dashboard,
                    ],
                    className="nav",
                ),
            ],
            className="header",
        ),
    ]
)

anticipate_simulate_layout = anticipate_simulate_layout.create_layout()
dashboard_layout = dashboard.app_layout
anticipate_simulate_callbacks.register_callbacks(app)

# Create the app layout
content = html.Div(id="page-content", children=[
    html.Div([
        dcc.Checklist(
            id={"type": "skill-checkbox", "category": category}
        ) for category, _ in app_utils.get_categories_skills().items()
    ]),
    html.Div([
        app_utils.create_toggle_switch(),
        html.Div(id="selected-skills-output", className='pretty_container'),
        html.Div(id="mode-content", children=[
            app_utils.create_probability_chart(),
            dcc.RadioItems(id="job-radio"),
            html.Div(id="loading-output"),
            html.Div(id="simulated-skills-output"),
            html.Div(id='current-target-job')
        ])])

])
app.layout = html.Div([dcc.Location(id="url"), index_layout, content])


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"))
def render_page_content(pathname):
    if pathname == "/":
        return anticipate_simulate_layout
    elif pathname == "/dashboard":
        return dashboard_layout
    elif pathname == "/predict-simulate":
        return anticipate_simulate_layout

    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
