from dash import Dash, dcc, html
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plots
from screeninfo import get_monitors
import plots

app = dash.Dash(__name__)
total_employers = len(plots.survey)
part_time, freelancer = plots.binarize(plots.survey, 'Employment')[['Employed_part-time',
                                                                    'Independent contractor_freelancer_or self-employed']].sum().values

app_layout = html.Div([
    html.Div([
        html.Div([
            html.H2(f"{total_employers}", style={'font-size': '30px'}),
            html.P("No. of survey respondents"),
            html.Div(className="color-box top_header", style={"background-color": "#2ca02c"})
        ], className="pretty_container ", style={'width': '31%', 'float': 'left'}),

        html.Div([
            html.H2(f"{part_time}", style={'font-size': '30px'}),
            html.P("No. of part-time employees"),
            html.Div(className="color-box top_header", style={"background-color": "#1f77b4"})
        ], className="pretty_container", style={'width': '31%', 'float': 'left'}),

        html.Div([
            html.H2(f"{freelancer}", style={'font-size': '30px'}),
            html.P("No. of freelancer employees"),
            html.Div(className="color-box top_header", style={"background-color": "#d62728"})
        ], className="pretty_container", style={'width': '31%', 'float': 'left'}),

        # html.P("Anticipate my job and simulate more skills",
        #        className='pretty_container four columns'),
    ], className="row")
])

app.layout = app_layout

if __name__ == "__main__":
    app.run_server(debug=True)
