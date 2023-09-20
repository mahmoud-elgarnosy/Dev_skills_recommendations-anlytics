import notebooks.prediction_utils as utils
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
from src.load_data import DataLoaderSingleton
from src import singelton_model

script_dir = os.path.dirname(os.path.abspath(__file__))
LOAD_PATH = '../data/interim/'
LOAD_PATH = os.path.join(script_dir, LOAD_PATH)
LOAD_HEATMAP_PATH = os.path.join(LOAD_PATH, 'skills_heatmap.csv')
LOAD_RELATED_SKILLS = os.path.join(LOAD_PATH, 'related_skills.csv')
LOAD_SKILLS_CATEGORIES = os.path.join(LOAD_PATH, 'all_skills_categories.csv')
LOAD_CATEGORIES_SKILLS = os.path.join(LOAD_PATH, 'all_categories_skills.csv')

skills_dev_df = DataLoaderSingleton().skills_dev_df


def build_heatmap_dev_skills_df():
    try:
        developers_skills_scaling = pd.read_csv(LOAD_HEATMAP_PATH, index_col=[0])
    except:

        # create heatmap dataframe to know most related skills
        developers_skills = {}
        for dev_type in skills_dev_df['DevType']:
            mask = skills_dev_df['DevType'][dev_type] == 1
            developers_skills[dev_type] = skills_dev_df.loc[mask, :].drop('DevType', axis=1, level=0).mean() * 100

        developers_skills = pd.concat(developers_skills, axis=1).T

        # Standardize the developer skills data
        developers_skills_scaling = pd.DataFrame(StandardScaler().fit_transform(developers_skills))
        developers_skills_scaling.columns = pd.MultiIndex.from_tuples(developers_skills.columns)
        developers_skills_scaling.index = developers_skills.index
        developers_skills_scaling.columns = developers_skills_scaling.columns.droplevel(0)
        developers_skills_scaling.to_csv(LOAD_HEATMAP_PATH)

    return developers_skills_scaling


def get_all_related_skills():
    try:
        related_skills_job = pd.read_csv(LOAD_RELATED_SKILLS, index_col=[0])
    except:
        heatmap_dev_skills_df = build_heatmap_dev_skills_df()
        related_skills_job = {}
        for job in heatmap_dev_skills_df.index:
            dev_skills = heatmap_dev_skills_df.loc[job, :].sort_values(ascending=False)
            related_skills = dev_skills[dev_skills > .5]
            related_skills_job[job] = related_skills
        related_skills_job = pd.concat(related_skills_job, axis=1)
        related_skills_job.to_csv(LOAD_RELATED_SKILLS)
    return related_skills_job


def get_related_skills(target_jop, already_have_skills):
    related_skills_job = get_all_related_skills()
    related_skills = related_skills_job[target_jop].dropna().sort_values(ascending=False)
    related_skills = related_skills[~related_skills.index.isin(already_have_skills)].index
    return related_skills


def get_recommended_skills(target_job, already_have_skills):

    # Helper function to get model prediction
    def get_prediction(skills):
        df = utils.prepare_df(skills, features_names)
        predictions = utils.predict_roles(model, df, target_names)
        return predictions[target_job]

    # Get the loaded model and related skills
    model_loader = singelton_model.ModelLoaderSingleton()
    features_names, target_names, model = model_loader.features_names, model_loader.target_names, model_loader.model
    related_skills = get_related_skills(target_job, already_have_skills)

    # Calculate the base prediction
    base_prediction = get_prediction(already_have_skills)

    # Calculate the uplift in job prediction for each skill when added to existing skills
    uplifts = {}
    for skill in related_skills:
        new_skills = already_have_skills + [skill]
        skill_prediction = get_prediction(new_skills)
        uplift = (skill_prediction - base_prediction) / base_prediction
        uplifts[skill] = uplift

    # Sort skills by uplift and choose the top 10
    sorted_uplifts = pd.Series(uplifts, name='uplift_skill').sort_values(ascending=False)
    chosen_skills = sorted_uplifts.index[:10]

    # Calculate predictions with chosen skills and final predictions
    chosen_skills_prediction = get_prediction(chosen_skills)
    final_prediction = get_prediction(already_have_skills + list(chosen_skills))

    # Apply conditions to adjust chosen_skills
    if final_prediction < 0.98 or chosen_skills_prediction < 0.60:
        chosen_skills = sorted_uplifts.index[:15]
    elif final_prediction > 0.95 and chosen_skills_prediction < 0.15:
        chosen_skills = sorted_uplifts.index[:2]
    return chosen_skills


def get_all_skills():
    df_columns = skills_dev_df.drop('DevType', axis=1, level=0).columns
    categories = set(df_columns.get_level_values(level=0))
    categories_skills = {c: list(skills_dev_df[c].columns) for c in categories}

    try:
        all_skills = pd.read_csv(LOAD_SKILLS_CATEGORIES, index_col=[0])
    except:
        # Create a dictionary of all skills
        all_skills_dict = {}
        for category, skill in df_columns:
            all_skills_dict[skill] = category

        # Convert the dictionary to a DataFrame and save it as a CSV
        all_skills = pd.DataFrame([all_skills_dict])
        all_skills.to_csv(LOAD_SKILLS_CATEGORIES)

    return all_skills, categories, categories_skills


def get_recommended_categories(target_job, already_have_skills):
    # Get recommended skills for the target job
    recommended_skills = get_recommended_skills(target_job, already_have_skills)

    # Get all skills and categories
    all_skills, categories, _ = get_all_skills()

    # Initialize a dictionary to store recommended categories
    recommended_categories = {category: [] for category in categories}

    # Categorize recommended skills
    for skill in recommended_skills:
        skill_category = all_skills[skill].iloc[0]
        recommended_categories[skill_category].append(skill)

    return recommended_categories


def get_all_jobs():
    return list(skills_dev_df['DevType'].columns)
