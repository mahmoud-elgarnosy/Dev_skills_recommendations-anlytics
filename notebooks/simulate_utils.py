import notebooks.prediction_utils as utils
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
from src.load_data import DataLoaderSingleton
from src import singelton_model

# script_dir = os.path.dirname(os.path.abspath(__file__))
# LOAD_PATH = '../data/interim/'
# LOAD_PATH = os.path.join(script_dir, LOAD_PATH)
# LOAD_SKILLS_DEV = '7.0-Chosen_features_and_roles.pkl'
# LOAD_SKILLS_DEV_CSV = '7.0-Chosen_features_and_roles.csv'
# skills_dev_df = pd.read_csv(LOAD_PATH + LOAD_SKILLS_DEV_CSV, header=[0, 1], skipinitialspace=True)
# skills_dev_df.columns = pd.MultiIndex.from_tuples(skills_dev_df.columns)
skills_dev_df = DataLoaderSingleton().skills_dev_df


def build_heatmap_dev_skills_df():
    developers_skills = {}
    for dev_type in skills_dev_df['DevType']:
        mask = skills_dev_df['DevType'][dev_type] == 1
        developers_skills[dev_type] = skills_dev_df.loc[mask, :].drop('DevType', axis=1, level=0).mean() * 100

    developers_skills = pd.concat(developers_skills, axis=1).T
    developers_skills_scaling = pd.DataFrame(StandardScaler().fit_transform(developers_skills))
    developers_skills_scaling.columns = pd.MultiIndex.from_tuples(developers_skills.columns)
    developers_skills_scaling.index = developers_skills.index
    developers_skills_scaling.columns = developers_skills_scaling.columns.droplevel(0)

    return developers_skills_scaling


def get_related_skills(target_jop, already_have_skills):
    heatmap_dev_skills_df = build_heatmap_dev_skills_df()
    dev_skills = heatmap_dev_skills_df.loc[target_jop, :].sort_values(ascending=False)
    related_skills = dev_skills[dev_skills > 1]
    related_skills = related_skills[~related_skills.index.isin(already_have_skills)].index
    return related_skills


def get_recommended_skills(target_jop, already_have_skills):
    already_have_skills_list = already_have_skills.copy()
    loaded_model = singelton_model.ModelLoaderSingleton()
    features_names, target_names, model = loaded_model.features_names, loaded_model.target_names, loaded_model.model
    related_skills = get_related_skills(target_jop, already_have_skills_list)
    recommended_skills = []
    df = utils.prepare_df(already_have_skills_list, features_names)
    predictions = utils.predict_roles(model, df, target_names)
    base_prediction = predictions[target_jop]

    while (base_prediction < .90) or (len(recommended_skills) < 8):
        most_related_skills = {}
        for skill in related_skills:
            new_skills = already_have_skills_list + [skill]
            df = utils.prepare_df(new_skills, features_names)
            predictions = utils.predict_roles(model, df, target_names)
            skill_prediction = predictions[target_jop]

            uplift_skill_prediction = (skill_prediction - base_prediction) / base_prediction
            most_related_skills[skill] = [uplift_skill_prediction, skill_prediction]
        most_related_skills = pd.DataFrame.from_dict(most_related_skills,
                                                     orient='index',
                                                     columns=['uplift_skill', 'skill_prediction']).sort_values(
            by='uplift_skill',
            ascending=False)
        if most_related_skills.empty:
            break
        base_prediction = most_related_skills['skill_prediction'].values[0]
        most_related_skill = most_related_skills.index.values[0]

        # print(target_jop, most_related_skill, most_related_skills['skill_prediction'].values[0],
        #       most_related_skills['uplift_skill'].values[0])

        related_skills = list(related_skills)
        related_skills.remove(most_related_skill)
        already_have_skills_list += [most_related_skill]
        recommended_skills += [most_related_skill]

        if len(recommended_skills) > 10:
            break

    return recommended_skills


def get_all_skills():
    df_columns = skills_dev_df.drop('DevType', axis=1, level=0).columns
    categories = set(df_columns.get_level_values(level=0))
    all_skills = list(df_columns)
    all_skills = [(sub[1], sub[0]) for sub in all_skills]
    all_skills = dict(all_skills)
    categories_skills = {c: list(skills_dev_df[c].columns) for c in categories}
    return all_skills, categories, categories_skills


def get_recommended_categories(target_jop, already_have_skills):
    recommended_skills = get_recommended_skills(target_jop, already_have_skills)

    all_skills, categories, _ = get_all_skills()
    recommended_categories = {key: [] for key in categories}
    for skill in recommended_skills:
        skill_category = all_skills[skill]
        recommended_categories[skill_category].append(skill)

    return recommended_categories


def get_all_jobs():
    return list(skills_dev_df['DevType'].columns)
