from dash import dcc, html
import plotly.express as px
from dash_iconify import DashIconify
import dash_daq as daq
from notebooks import prediction_utils, simulate_utils


def get_jobs_predictions(selected_skills):
    features_names, target_names, model = prediction_utils.fetch_best_model_data()
    df = prediction_utils.prepare_df(selected_skills, features_names)
    predictions = prediction_utils.predict_roles(model, df, target_names)
    return predictions


def get_categories_skills():
    """
    Get the skills categories and skills using simulate_utils.

    Returns:
        dict: A dictionary containing skills categories and skills.
    """
    _, _, categories_skills = simulate_utils.get_all_skills()
    categories_skills = {"Languages": categories_skills["Languages"], **categories_skills}
    return categories_skills


def get_icon(skill: str):
    """
    Generate DashIconify component for a skill icon.

    Args:
        skill (str): The name of the skill.

    Returns:
        DashIconify: A DashIconify component representing the skill icon.
    """
    skill = (skill.replace('-', '')
             .replace(' ', '')
             .replace('+', 'plus')
             .replace('.js', 'js')
             .replace('.', 'dot-'))
    if '/' in skill:
        if skill == 'Bash/Shell':
            skill = skill.split('/')[0]
        else:
            skill = skill.split('/')[1]
    return DashIconify(icon=f"devicon:{skill.lower()}")


def get_checklist(category, skills):
    """
    Create a checklist of skills checkboxes for a given category.

    Args:
        category (str): The category of skills.
        skills (list): List of skills in the category.

    Returns:
        dcc.Checklist: A Dash checklist component for skills selection.
    """
    return dcc.Checklist(
        id={"type": "skill-checkbox", "category": category},
        options=[{'label': [get_icon(skill), skill.replace('(Delphi_C++ Builder)', '')], 'value': skill} for skill in
                 skills],
        value=[],
        style={'verticalAlign': 'top', 'width': '100%', 'display': 'flex', 'flexWrap': 'wrap', 'margin': 'auto'},
        labelStyle={'fontSize': '14px', 'margin': '5px'},
        inline=True
    )


def create_toggle_switch():
    """
    Create a toggle switch for switching between job prediction and skill simulation modes.

    Returns:
        html.Div: A Div containing the toggle switch and labels.
    """
    return html.Div([
        html.H3(f"Predict jobs", style={'display': 'inline-block'}),
        daq.ToggleSwitch(
            id='toggle-switch',
            value=False,
            color="green",
            label='',
            labelPosition='bottom',
            size=40,
            style={'display': 'inline-block'}
        ),
        html.H3(f"Simulate skills", style={'display': 'inline-block'})],
        style={'text-align': 'center', 'margin': 'auto'})


def create_simulate_skills_content():
    """
    Create the content for simulating skills selection.

    Returns:
        html.Div: A Div containing elements for simulating skills.
    """
    return \
        html.Div(children=[
            html.Div([html.H2('Select a target job', style={'text-align': 'center'}),
                      dcc.RadioItems(
                          id="job-radio",
                          options=simulate_utils.get_all_jobs(),
                          value=None,
                          style={'margin': '10px', 'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)'},
                          labelStyle={'fontSize': '12px', 'margin': '2px'},
                      )], className='pretty_container'),
            # html.Div(id='current-target-job', className='pretty_container'),
            html.Div([html.Div(id="simulated-skills-output"),
                      dcc.Loading(
                          id="loading-output",
                          type="circle")
                      ], className='pretty_container')
        ])


def create_current_target_dev(current_job, target_job):
    """
    Create html dev for current and target job

    Args:
        current_job (str, optional): the expected current job, Defaults to "None".
        target_job ((str, optional): the selected target job, Defaults to "None".

    Returns:
        html.Div: A Div the current and the expected job.
    """
    return html.Div([html.H2('Your current and target job', style={'textAlign': 'center'}),
                     html.Div([html.Strong(f"Your expected current job: "), html.Span(current_job)]),
                     html.Div([html.Strong(f"Your target job: "), html.Span(target_job)]),
                     html.Br()])


def create_selected_simulated_skills(selected_skills_dict, header="Selected skills",
                                     current_job=None, target_job=None):
    """
    Create the output displaying selected or simulated skills.

    Args:
        selected_skills_dict (dict): A dictionary of selected skills per category.
        header (str, optional): The header text. Defaults to "Selected skills".
        current_job (str, optional): the expected current job, Defaults to "None".
        target_job ((str, optional): the selected target job, Defaults to "None".

    Returns:
        list: A list of HTML elements representing the selected skills output.
    """
    output_children = [html.H2(header, style={'textAlign': 'center'})]
    if current_job and target_job:
        output_children += [html.Div([html.Strong(f"Your expected current job: "), html.Span(current_job)]),
                            html.Div([html.Strong(f"Your target job: "), html.Span(target_job)]),
                            html.Br(),
                            html.Strong('You should learn following skills', style={'text-align': 'center'})]

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


def create_min_max_skills_header():
    """
    Create the header indicating the skill selection range.

    Returns:
        html.Div: A Div containing the header.
    """
    return html.Div(
        id="min-max-skills-header",
        children=[html.H3("Select between 3 and 30 skills", style={'textAlign': 'center'})]
    )


def create_message_output():
    """
    Create the output for displaying messages.

    Returns:
        html.Div: A Div for displaying messages.
    """
    return html.Div(id="message-div", className="message-output")


def create_probability_chart():
    """
    Create the probability chart section.

    Returns:
        html.Div: A Div containing the probability chart and related elements.
    """
    return html.Div(
        id="chart-container",
        className='pretty_container',
        children=[
            html.H2('Current job expectations', style={'textAlign': 'center'}),
            create_message_output(),
            dcc.Graph(id="probability-chart"),
        ],
    )


def plot_predictions_jobs(predictions, threshold=10):
    """
    Create a bar plot for job predictions.

    Args:
        predictions (pd.DataFrame): Predicted job probabilities.
        threshold (int, optional): Number of bars to display. Defaults to 10.

    Returns:
        plotly.graph_objs: A Plotly figure for the job predictions.
    """
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
