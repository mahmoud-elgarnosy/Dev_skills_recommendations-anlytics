import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from notebooks import prediction_utils
from notebooks import simulate_utils
from dash_iconify import DashIconify

app = dash.Dash(__name__)

# Sample skill categories and skills
_, _, categories_skills = simulate_utils.get_all_skills()


def get_icon(skill: str):
    skill = skill.replace('-', '').replace(' ', '').replace('+', 'plus')
    if '/' in skill:
        skill = skill.split('/')[1]
    icon = DashIconify(
        icon=f"devicon:{skill.lower()}")
    if icon:
        return icon
    else:
        return DashIconify(
            icon=f"logos:{skill.lower()}")


def get_checklist(category, skills):
    if category in ['Languages']:
        return dcc.Checklist(
            id={"type": "skill-checkbox", "category": category},
            options=[{'label': [get_icon(skill), skill], 'value': skill} for skill in skills],
            value=[],
            style={'margin': '10px', 'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)'},
            labelStyle={'fontSize': '14px', 'margin': '5px'}
        )
    else:
        return dcc.Checklist(
            id={"type": "skill-checkbox", "category": category},
            options=[{'label': [get_icon(skill), skill], 'value': skill} for skill in skills],
            value=[],
            style={'margin': '10px', 'verticalAlign': 'top'},
            labelStyle={'fontSize': '14px', 'margin': '5px'}
        )


app.layout = html.Div([
    html.H1("Job Category Predictor", style={'textAlign': 'center'}),

    # Checkbox section for each category
    html.Div(id="skill-checkboxes", children=[
        html.Div([
            html.H3(category, style={'textAlign': 'center'}),
            get_checklist(category, skills),
        ])
        for category, skills in categories_skills.items()],
             style={'width': '80%', 'display': 'flex', 'flexWrap': 'wrap', 'margin': 'auto'}),

    # Bar chart section
    dcc.Graph(id="probability-chart"),
])


@app.callback(
    Output("probability-chart", "figure"),
    [Input({"type": "skill-checkbox", "category": category}, "value")
     for category in categories_skills.keys()]
)
def update_chart(*selected_skills):
    if all(skill_list is None for skill_list in selected_skills):
        return {}

    selected_skills = [skill for skills in selected_skills for skill in (skills or [])]
    print(selected_skills)

    if selected_skills:
        # Replace this part with your model's prediction logic
        # For demonstration purposes, using sample predicted probabilities
        features_names, target_names, model = prediction_utils.fetch_best_model_data()
        df = prediction_utils.prepare_df(selected_skills, features_names)
        predictions = prediction_utils.predict_roles(model, df, target_names)

        categories, probabilities = predictions.iloc[:10].index, predictions.iloc[:10].values

        # Create a bar chart
        # Create a customized bar chart
        fig = go.Figure(data=[go.Bar(y=categories, x=probabilities, orientation='h')],
                        layout=dict(title='Predicted Developer Jobs', xaxis_title='Probability', yaxis_title='Job'))

        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),  # Add margins around the chart
            paper_bgcolor='rgb(243, 243, 243)',  # Set background color
            plot_bgcolor='rgb(243, 243, 243)',  # Set plot area color
        )
        return fig
    else:
        return {}


if __name__ == "__main__":
    app.run_server(debug=True)
