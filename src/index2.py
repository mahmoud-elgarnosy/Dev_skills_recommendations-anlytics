import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from src import app_utils
import numpy as np

app = dash.Dash(__name__)

categories_skills = app_utils.get_categories_skills()

# Define the layout of your app with multiple sections
app.layout = html.Div([
    *[
        html.Div([
            html.Div(
                html.H2(f"{category} ▶", id=f"toggle-arrow-{i}", className="title"),
                id=f"section-header-{i}-container"),
            html.Div(id=f"content-{i}", style={'display': 'flex', 'align-items': 'center'}),
            # Store component to keep track of checkbox states for each section
            dcc.Store(id=f"checkbox-states-{i}", data={})
        ], id=f"section-{i}") for i, category in enumerate(categories_skills.keys(), start=1)
    ],

    # Store component to keep track of open section
    dcc.Store(id='open-section', data=None)
])

# Initialize content states
content_states = {key: False for key in categories_skills.keys()}


# Callback to update open section when a section header is clicked
@app.callback(
    Output("open-section", "data"),
    [Input(f"section-header-{i}-container", "n_clicks") for i in range(1, len(categories_skills.keys()) + 1)],
)
def update_open_section(section1_clicks, section2_clicks, section3_clicks, section4_clicks, section5_clicks,
                        section6_clicks, section7_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return None

    clicked_section = ctx.triggered[0]["prop_id"].split(".")[0]
    section_id = int(clicked_section.split("-")[-2])

    return section_id


# Callback to toggle the content and arrow icon
@app.callback(
    [Output(f"content-{i}", "children") for i in range(1, len(categories_skills.keys()) + 1)],
    [Output(f"toggle-arrow-{i}", "children") for i in range(1, len(categories_skills.keys()) + 1)],
    Input("open-section", "data"),
    [State(f"checkbox-states-{i}", "data") for i in range(1, len(categories_skills.keys()) + 1)]
)
def toggle_content(open_section, *checkbox_states):
    if open_section is None:
        return [None for i in range(1, len(categories_skills.keys()) + 1)] + [f"{category} ▶" for category in
                                                                              categories_skills.keys()]

    for section_id in content_states:
        content_states[section_id] = False
    content_states[list(categories_skills.keys())[open_section - 1]] = not content_states[
        list(categories_skills.keys())[open_section - 1]]

    contents = ["" for i in range(len(categories_skills))]
    idx = np.where(list(content_states.values()))[0]
    idx = int(idx[0])
    category = list(categories_skills.keys())[idx]
    skills = categories_skills[category]
    contents[idx] = app_utils.get_checklist(category, skills)

    arrow_symbols = [f"{category} ▶" for category in categories_skills.keys()]  # Right arrow
    arrow_symbols[open_section - 1] = arrow_symbols[open_section - 1].replace('▶', "▼")  # Down arrow

    # Update checkbox states for the current section
    checkbox_states[open_section - 1] = checkbox_states[category]

    return *contents, *arrow_symbols


if __name__ == "__main__":
    app.run_server(debug=True)
