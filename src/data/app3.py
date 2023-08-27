from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plots


# Iris bar figure
def drawFigure(figure, width, height):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=figure.update_layout(
                        width=width,
                        height=height,
                        # template='ggplot2',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    )
                )
            ])
        ),
    ])


# Text field
def drawText():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div(
                    [html.H5("No. of Dislikes", style={"font-weight": "bold"})],
                    className="control_Panel",
                    style={"text-align": "center", "vertical-align": "middle"}
                ),
            ])
        ),
    ])


# Data
df = px.data.iris()

# Build App
app = Dash()

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    drawFigure(plots.create_most_used_languages_chart(), 1200, 400)
                ], width=3, className='pretty_container'
                ),
                dbc.Col([
                    drawFigure(plots.create_gender_dist_chart(plots.count_gender()), 450, 400),
                ], width=6, className='pretty_container'),
            ], style={'text-align': 'center'}),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(plots.create_gender_dist_chart(plots.count_gender()), 450, 400)
                ], width=3, className='pretty_container'
                ),
                dbc.Col([
                    drawFigure(plots.create_employment_vs_dev_type_chart(plots.calculate_most_common_jobs(10)), 1200, 400)
                ], width=3, className='pretty_container'),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(plots.create_jobs_salaries_chart(), 1450, 300)
                ], width=9, className='pretty_container'),
                dbc.Col([
                    drawFigure(plots.create_jobs_salaries_chart(), 450, 300)
                ], width=3, className='pretty_container'),
            ], align='center'),
        ]), color='dark'
    )
])

# Run app and display result inline in the notebook
app.run_server()
