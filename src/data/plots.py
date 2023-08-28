import os
import pickle
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
LOAD_PATH = os.path.join(script_dir, '../../data/interim/')
LOAD_ANALYSIS_DF = '4.0-preprocessed-data-analysation.pkl'
LOAD_SKILLS_DEV = '7.0-Chosen_features_and_roles.pkl'
survey = pd.read_pickle(LOAD_PATH + LOAD_ANALYSIS_DF)
skills_dev_df = pd.read_pickle(LOAD_PATH + LOAD_SKILLS_DEV)

with open(LOAD_PATH + 'chosen_columns.pkl', 'rb') as f:
    chosen_columns = pickle.load(f)

survey = survey[chosen_columns['analysis']]


# Helper Functions
def binarize(df, column):
    binarizer = MultiLabelBinarizer()
    mask = df[column].notnull()

    # filter by boolean indexing
    arr = binarizer.fit_transform(df.loc[mask, column])

    # create DataFrame and add missing (NaN)s index values
    return (pd.DataFrame(arr, index=df.index[mask], columns=binarizer.classes_)
            .reindex(df[column].index, fill_value=0))


def change_labels(x: str):
    if 'Developer_' in x:
        x = x.replace('Developer_', '') + ' dev'

    if ' or ' in x:
        if x == 'embedded applications or devices dev':
            x = 'Embedded applications dev'
        else:
            index_to_delete = x.index(' or ')
            x = x[index_to_delete + 4:]

    if 'Engineer_' in x:
        x = x.replace('Engineer_', '') + '  Engineer'

    if x.__contains__('back_end') or x.__contains__('full_stack'):
        x += ' dev'
    return x.capitalize()


# 1.Employment vs Dev type
# first we need to know Employment type abd is there any relation between them with dev type or not
def calculate_most_common_jobs(threshold=10):
    jobs_freq = skills_dev_df['DevType'].sum().reset_index()
    jobs_freq.columns = ['job_type', 'freq']
    jobs_freq = jobs_freq.sort_values(by='freq', ascending=False)
    filtering = (jobs_freq.job_type.str.contains('full_stack')) | (jobs_freq.job_type.str.contains('back_end'))
    job_freq_without_specific_titles = jobs_freq[~filtering]
    most_10_freq_jobs = list(job_freq_without_specific_titles.iloc[:threshold].sort_values(by='freq').job_type)
    return most_10_freq_jobs


def calculate_employment_dev_count_percentage(dev_types):
    # Define employment types
    employment_columns = {
        'full-time': 'Employed_full-time',
        'part-time': 'Employed_part-time',
        'freelancer': 'Independent contractor_freelancer_or self-employed'
    }

    # Prepare employment data
    employment_df = binarize(survey, 'Employment')
    employment_df = employment_df[list(employment_columns.values())]
    employment_df.rename(columns=employment_columns, inplace=True)
    employment_df.columns = pd.MultiIndex.from_product([['Employment'], employment_df.columns])

    # Prepare developer data
    dev_df = skills_dev_df['DevType'][dev_types]
    dev_df.columns = pd.MultiIndex.from_product([['DevType'], dev_df.columns])

    # Merge employment and developer data
    employment_dev = employment_df.merge(dev_df, left_index=True, right_index=True)

    # Calculate employment vs. developer counts
    employment_dev_count = (employment_dev.Employment.values.T @ employment_dev.DevType)
    employment_dev_count.index = employment_columns.keys()
    # Calculate percentages
    employment_dev_percentage = (employment_dev_count / employment_dev_count.sum(axis=0)) * 100
    employment_dev_percentage = employment_dev_percentage.drop('full-time', axis=0)

    return employment_dev_count, employment_dev_percentage


def create_employment_vs_dev_type_chart(dev_types):
    employment_dev_count, employment_dev_percentage = calculate_employment_dev_count_percentage(dev_types)

    # Create the figure
    fig = go.Figure()

    # Get the viridis color scale
    # colorscale = px.colors.qualitative.Dark24

    for i, employment_type in enumerate(employment_dev_percentage.index):
        fig.add_trace(go.Bar(
            name=employment_type,
            y=dev_types,
            x=employment_dev_percentage.loc[employment_type, :].values,
            orientation='h',
            # marker_color=colorscale[i % len(colorscale)]  # Cycle through viridis colors
        ))
    # Set layout
    layout = go.Layout(
        barmode='group',
        title=dict(
            text="Most Common Jobs vs Employment Type",
            font_size=20,
            x=.5
        ),
    )

    fig.update_layout(layout)
    fig.update_yaxes(title="Job Type",
                     tickmode='array',
                     tickvals=np.arange(len(dev_types)),
                     ticktext=[change_labels(x) for x in dev_types],
                     tickangle=45,
                     tickfont=dict(family='Rockwell', size=15))

    fig.update_xaxes(title="Percentage (%)",
                     tickfont={'size': 20})

    return fig


# 2. most common languages
def create_most_used_languages_chart():
    # extract most 10 used programing languages that used in development
    language_have_worked_with = binarize(survey, 'LanguageHaveWorkedWith')
    most_used_languages = language_have_worked_with.sum(axis=0).sort_values(ascending=False).iloc[:5]
    most_used_languages_per = most_used_languages / len(survey)
    most_used_languages_per.name = 'used'

    # Extract those languages that the developer doesn't know and wants to know
    language_want_to_work_with = binarize(survey, 'LanguageWantToWorkWith')
    # filter them, I don't want the languages that chosen in both
    Languages = (language_have_worked_with * .5) + language_want_to_work_with
    Languages[Languages == 1.5] = 0
    most_planning_languages_per = Languages.sum(axis=0)[most_used_languages.index] / len(survey)
    most_planning_languages_per.name = 'planning to use'

    # concat_two_series
    df = pd.concat([most_used_languages_per, most_planning_languages_per], axis=1, names=['used', 'planning'])

    # Create the figure
    fig = go.Figure()

    # Get the viridis color scale
    # colorscale = px.colors.qualitative.Dark24

    for i, used_type in enumerate(df.columns):
        text = (df.loc[:, used_type].values * 100).astype(int)
        text = [f"{value}%" for value in text]

        fig.add_trace(go.Bar(
            name=used_type,
            y=df.index,
            x=(df.loc[:, used_type].values * 100).astype(int),
            orientation='h',
            text=text,
            # marker_color=colorscale[i % len(colorscale)]  # Cycle through viridis colors
        ))
    # Set layout
    layout = go.Layout(
        barmode='group',
        title=dict(
            text="Most Used Languages",
            font_size=20,
            x=.5
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01)
    )

    # Reverse the y-axis
    layout.yaxis['side'] = 'right'

    fig.update_layout(layout)
    fig.update_yaxes(title="Programing Languages",
                     tickmode='array',
                     tickvals=np.arange(len(df.index)),
                     ticktext=df.index,
                     tickangle=45,
                     tickfont=dict(family='Rockwell', size=15))

    fig.update_xaxes(title="Percentage (%)",
                     tickfont={'size': 20},
                     autorange="reversed")

    return fig


# 3. jobs salary
def create_jobs_salaries_chart():
    survey_comp = survey.copy()

    # we only need rows with one dev_type for fair comparison
    filteration = (skills_dev_df['DevType'].sum(axis=1) == 1)
    dev_type = skills_dev_df[filteration]['DevType'].idxmax(1)
    survey_comp = survey_comp.loc[dev_type.index, :]
    survey_comp['DevType'] = dev_type

    # we also need more filtration for salaries not equal nan
    survey_comp = survey_comp[~survey_comp['CompTotal'].isna()]

    # calculate median of years of experience and salaries
    dev_years = survey_comp.groupby('DevType')['YearsCodePro'].median().sort_values(ascending=False)
    dev_comp = survey_comp.groupby('DevType')['CompTotal'].median().sort_values(ascending=False)
    dev_years_comp = pd.concat([dev_comp, dev_years], axis=1)

    # plot figure
    fig = px.scatter(x=dev_years_comp.index,
                     y=dev_years_comp.CompTotal,
                     size=dev_years_comp.YearsCodePro.values,
                     labels={"size": "Experience years",
                             "x": "Job",
                             "y": "Salary"})
    layout = go.Layout(
        title=dict(
            text="Most Paid Jobs With Respect To Years Of Experience",
            font_size=20,
            x=.5),
        margin=dict(t=60, l=10, r=10, b=10)

    )

    fig.update_layout(layout)
    fig.update_yaxes(
        title="Salary",
        tickangle=45,
        tickfont=dict(family='Rockwell', size=15))
    fig.update_xaxes(
        title="Job Type",
        tickmode='array',
        tickvals=np.arange(len(dev_years_comp.index)),
        ticktext=[change_labels(x) for x in dev_years_comp.index],
        tickangle=45,
        tickfont=dict(family='Rockwell', size=12))

    return fig


# 4. Gender Distribution
def count_gender():
    gender_data = survey[survey['Gender'].isin([['Man'], ['Woman']])]
    gender_count = gender_data['Gender'].value_counts()
    return gender_count


def create_gender_dist_chart(gender_count):
    fig = px.pie(gender_count,
                 values=gender_count.values,
                 names=gender_count.index,
                 title='Gender Distribution')

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label')
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=.85,
            xanchor="right",
            x=.80
        ),
        margin=dict(t=30, l=10, r=10, b=10),
        title_font_size=20,
        title_x=0.5
    )

    return fig


# 5. Education vs job
# Function to create the education vs. job occupation chart
def create_education_vs_job_chart():
    # Mapping to rename education levels
    education_mapping = {
        'Master’s degree (M.A., M.S., M.Eng., MBA, etc.)': "Master's",
        'Bachelor’s degree (B.A., B.S., B.Eng., etc.)': "Bachelor's",
        'Some college/university study without earning a degree': "Some College",
        'Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)': "Secondary School",
        'Something else': "Unknown",
        'Primary/elementary school': "Primary School",
        'Professional degree (JD, MD, etc.)': "Professional Degree",
        'Associate degree (A.A., A.S., etc.)': "Associate Degree",
        'Other doctoral degree (Ph.D., Ed.D., etc.)': "Other Doctoral",
        float('nan'): "Unknown"
    }

    # Extract education levels from the survey data and apply the mapping
    edu = survey['EdLevel']
    edu = edu.map(education_mapping)

    # Specify the custom order of education levels for sorting
    custom_order = [
        "Primary School", "Secondary School", "Some College",
        "Associate Degree", "Bachelor's", "Master's", "Professional Degree",
        "Other Doctoral", "Something Else", "Unknown"
    ]

    # Sort education levels and remove 'Unknown'
    edu = edu.sort_values()
    edu = edu[~(edu == 'Unknown')]

    # Extract job types from skills_dev_df
    dev = skills_dev_df['DevType']

    # Merge education levels and job types data
    melted_df = pd.merge(edu, dev, left_index=True, right_index=True).melt(id_vars=["EdLevel"], var_name="Job",
                                                                           value_name="Occupation")

    # Group data by education level and job type, and calculate percentage works
    grouped_df = melted_df.groupby(["EdLevel", "Job"])["Occupation"].sum().reset_index()

    # Calculate percentage of EduLevel within job type
    jobs_freq = melted_df.groupby('Job').sum(numeric_only=True)
    repeated_df = pd.concat([jobs_freq] * 8)
    # make sure both index are same
    grouped_df.index = grouped_df.Job
    grouped_df['Occupation'] = grouped_df['Occupation'] * 100 / repeated_df['Occupation']

    text = (grouped_df['Occupation']).astype(int)
    text = [f"{value}%" for value in text]

    # Create a bar chart using Plotly Express
    fig = px.bar(
        grouped_df,
        x="Job",
        y="Occupation",
        color="EdLevel",
        labels={"Occupation": "Percentage (%)"},
        category_orders={"EdLevel": custom_order},
        text=text,
    )

    # Customize layout using Plotly graph objects
    layout = go.Layout(
        title=dict(
            text="Education Level vs. Job Occupation",
            font_size=20,
            x=.5),
        margin=dict(t=60, l=10, r=10, b=10)
    )

    fig.update_layout(layout)
    fig.update_traces(textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
    fig.update_yaxes(
        title="Percentage (%)",
        tickangle=45,
        tickfont=dict(family='Rockwell', size=15))
    fig.update_xaxes(
        title="Job Type",
        tickmode='array',
        tickvals=np.arange(len(jobs_freq.index)),
        ticktext=[change_labels(x) for x in jobs_freq.index],
        tickangle=45,
        tickfont=dict(family='Rockwell', size=15))

    return fig


# 6. Country Distribution
def create_country_dist_chart():
    # check the respondens by "Country"
    top10_country = survey['Country'].value_counts().head(10)

    top10_country = top10_country.rename({
        'United States of America': 'USA',
        'United Kingdom of Great Britain and Northern Ireland': 'Britain'
    })

    fig = px.pie(
        top10_country,
        values=top10_country.values,
        names=top10_country.index,
        title='Top 10 Country Distribution')
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label')
    fig.update_layout(
        margin=dict(t=30, l=10, r=10, b=10),
        title_font_size=20,
        title_x=0.5,
        showlegend=False)

    return fig
