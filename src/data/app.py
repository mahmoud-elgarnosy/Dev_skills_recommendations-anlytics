import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from dash_iconify import DashIconify
app = dash.Dash(__name__)


# Replace this with your machine learning module
def load_model():
    return None


def predict_jobs(selected_skills, model):
    return {}  # Replace this with your prediction logic


model = load_model()

app.layout = html.Div([
    html.H1("Developer Job Predictor", style={'textAlign': 'center'}),
    dcc.Checklist(
        options=[
            {"label": [
                DashIconify(
                    icon="devicon:python", width=50),
                html.Span("Python", style={"font-size": 20, "padding-left": 5}),
            ],
                "value": "AAPL",
            },
            {
                "label": DashIconify(icon="logos:facebook", style={"marginRight": 16}),
                "value": "FB",
            },
            {
                "label": DashIconify(icon="logos:netflix", style={"marginRight": 16}),
                "value": "NFLX",
            },
            {
                "label": DashIconify(icon="logos:microsoft", style={"marginRight": 16}),
                "value": "MSFT",
            },
        ],
        value=["AAPL", "FB", "NFLX"], id='skill-checkboxes'
    ),
    dcc.Graph(id='bar-chart', style={'margin': '10px'})
])


@app.callback(
    Output('bar-chart', 'figure'),
    [Input('skill-checkboxes', 'value')]
)
def update_bar_chart(selected_skills):
    job_probabilities = {'dsfa': .75, 'dssfa': .35, 'dsfadf': .45, 'dsfaxd': .65, 'dsfawe': .4, 'dsfsadfa': .75}

    job_names = list(job_probabilities.keys())
    probabilities = list(job_probabilities.values())

    fig = go.Figure(data=[go.Bar(y=job_names, x=probabilities, orientation='h')],
                    layout=dict(title='Predicted Developer Jobs', xaxis_title='Probability', yaxis_title='Job'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
