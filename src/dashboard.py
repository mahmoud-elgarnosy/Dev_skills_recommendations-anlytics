from dash import Dash, dcc, html
import dash
from src import plots

total_employers = len(plots.survey)
part_time, freelancer = plots.binarize(plots.survey, 'Employment')[['Employed_part-time',
                                                                    'Independent contractor_freelancer_or self-employed']].sum().values


def create_summary_banner():
    return html.Div([
        html.Div([
            html.H2(f"{total_employers}", style={'font-size': '30px'}),
            html.P("No. of survey respondents"),
            html.Div(className="color-box top_header", style={"background-color": "#66c2a5"})
        ], className="pretty_container ", style={'width': '32%', 'float': 'left'}),

        html.Div([
            html.H2(f"{part_time}", style={'font-size': '30px'}),
            html.P("No. of part-time employees"),
            html.Div(className="color-box top_header", style={"background-color": "#3366cc"})
        ], className="pretty_container", style={'width': '32%', 'float': 'left'}),

        html.Div([
            html.H2(f"{freelancer}", style={'font-size': '30px'}),
            html.P("No. of freelancer employees"),
            html.Div(className="color-box top_header", style={"background-color": "#d62728"})
        ], className="pretty_container", style={'width': '32%', 'float': 'left'}),

    ], className="row")


def create_figure(figure):
    figure.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return figure


app_layout = html.Div([
    html.H2("Dashboard", style={'textAlign': 'center'}, className='title'),
    create_summary_banner(),
    html.Div(
        [
            html.Div(
                [dcc.Graph(id="fig1", figure=create_figure(plots.create_most_used_languages_chart()))],
                className="pretty_container2 three columns",
            ),
            html.Div(
                [dcc.Graph(id="fig2",
                           figure=create_figure(
                               plots.create_employment_vs_dev_type_chart(plots.calculate_most_common_jobs())))],
                className="pretty_container2 nine columns",
            ),
        ],
        className="row flex-display",
    ),

    html.Div(
        [
            html.Div(
                [dcc.Graph(id="fig5", figure=create_figure(plots.create_education_vs_job_chart()))],
                className="pretty_container2 nine columns",
            ),
            html.Div(
                [dcc.Graph(id="fig6",
                           figure=create_figure(plots.create_gender_dist_chart(plots.count_gender())))],
                className="pretty_container three columns",
            ),
        ],
        className="row flex-display",
    ),

    html.Div(
        [
            html.Div(
                [dcc.Graph(id="fig3", figure=create_figure(plots.create_country_dist_chart()))],
                className="pretty_container2 three columns",
            ),
            html.Div(
                [dcc.Graph(id="fig4", figure=create_figure(plots.create_jobs_salaries_chart()))],
                className="pretty_container2 nine columns",
            ),
        ],
        className="row flex-display",
    ),

])


# app = dash.Dash(__name__)
# app.layout = app_layout
#
# if __name__ == "__main__":
#     app.run_server(debug=True)
