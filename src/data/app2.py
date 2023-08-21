import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from dash_iconify import DashIconify
from notebooks import prediction_utils, simulate_utils

app = dash.Dash(__name__)

# Sample skill categories and skills
_, _, categories_skills = simulate_utils.get_all_skills()


def get_icon(skill: str):
    skill = skill.replace('-', '').replace(' ', '').replace('+', 'plus').replace('.js', 'js').replace('.', 'dot-')
    if '/' in skill:
        if skill == 'Bash/Shell':
            skill = skill.split('/')[0]
        else:
            skill = skill.split('/')[1]
    return DashIconify(icon=f"devicon:{skill.lower()}")


def get_checklist(category, skills):
    return dcc.Checklist(
        id={"type": "skill-checkbox", "category": category},
        options=[{'label': [get_icon(skill), skill.replace('(Delphi_C++ Builder)', '')], 'value': skill} for skill in skills],
        value=[],
        style={'verticalAlign': 'top', 'width': '100%', 'display': 'flex', 'flexWrap': 'wrap', 'margin': 'auto'},
        labelStyle={'fontSize': '14px', 'margin': '5px'},
        inline=True
    )


def create_selected_skills_output(selected_skills_dict):
    output_children = [html.H2("Selected Skills", style={'textAlign': 'center'})]

    for category, skills in selected_skills_dict.items():
        if skills:
            skills_text = ", ".join(skills)
            category_header = html.Strong(f"{category}: ")
            skills_span = html.Span(skills_text)
            category_div = html.Div([category_header, skills_span])
            output_children.append(category_div)

    if not any(selected_skills_dict.values()):
        output_children.append("No skills selected.")

    return output_children


app.layout = html.Div([
    html.H1("Job Category Predictor", style={'textAlign': 'center'}),

    # Main container for the page
    html.Div(
        id="main-container",
        children=[
            # Control board on the left half
            html.Div(
                id="control-board",
                children=[
                    html.H2("Select Skills", style={'textAlign': 'center'}),
                    *[html.Div([
                        html.Div(html.H3(category, style={'textAlign': 'center'}), className='column-left'),
                        html.Div(get_checklist(category, skills), className='column-right'),
                    ], className='row', style={'width': '100%', 'margin': 'auto', 'paddingBottom': '10px', 'borderBottom': '1px solid #ccc'})
                        for category, skills in categories_skills.items()],
                ],
                style={'width': '60%', 'float': 'left'}
            ),

            # Chart section on the right half
            html.Div([
                html.Div(id="selected-skills-output", className='pretty_container'),
                html.Div(
                    id="chart-container",
                    className='pretty_container',
                    children=[
                        html.H2('Current job expectations', style={'textAlign': 'center'}),
                        dcc.Graph(id="probability-chart"),
                    ],
                ),

            ], style={'width': '45%', 'float': 'right'}),
        ],
        style={'width': '100%', 'display': 'flex', 'overflow': 'hidden'}
    )
])


@app.callback(
    Output("selected-skills-output", "children"),
    [Input({"type": "skill-checkbox", "category": category}, "value")
     for category in categories_skills.keys()]
)
def update_selected_skills(*selected_skills):
    selected_skills_dict = {category: skills for category, skills in zip(categories_skills.keys(), selected_skills)}
    return create_selected_skills_output(selected_skills_dict)


@app.callback(
    Output("probability-chart", "figure"),
    [Input({"type": "skill-checkbox", "category": category}, "value")
     for category in categories_skills.keys()]
)
def update_chart(*selected_skills):
    if all(skill_list is None for skill_list in selected_skills):
        return {}

    selected_skills = [skill for skills in selected_skills for skill in (skills or [])]

    if selected_skills:
        # Replace this part with your model's prediction logic
        # For demonstration purposes, using sample predicted probabilities
        features_names, target_names, model = prediction_utils.fetch_best_model_data()
        df = prediction_utils.prepare_df(selected_skills, features_names)
        predictions = prediction_utils.predict_roles(model, df, target_names)

        fig = plot_predictions_jobs(predictions, threshold=10)
        return fig
    else:
        return {}


def plot_predictions_jobs(predictions, threshold=20):
    limited_predictions = predictions[:threshold]
    text = (limited_predictions.values * 100).astype(int)
    text = [f"{value}%" for value in text]

    fig = px.bar(predictions,
                 x=limited_predictions.index,
                 y=limited_predictions.values,
                 orientation='v',
                 text=text,
                 color=limited_predictions.values,
                 range_color=[0, 1],
                 color_continuous_scale='Viridis',
                 )

    def change_labels(x: str):
        if 'Developer_' in x:
            x = x.replace('Developer_', '') + ' dev'

        if ' or ' in x:
            index_to_delete = x.index(' or ')
            x = x[index_to_delete + 4:]

        if 'Engineer_' in x:
            x = x.replace('Engineer_', '') + '  Engineer'

        if x.__contains__('back_end') or x.__contains__('full_stack'):
            x += ' dev'
        return x

    new_labels = list(map(change_labels, limited_predictions.index))
    fig.update_xaxes(tickvals=list(range(len(new_labels))),
                     ticktext=new_labels)

    fig.update_layout(
        yaxis_range=[0, 1],
        title_x=0.5, showlegend=False, yaxis_title=None,
        xaxis_title=None,
        yaxis=dict(tickfont={'size': 15}),
        xaxis=dict(tickfont={'size': 20}),
        title_font_size=20
    )

    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', size=10))

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
