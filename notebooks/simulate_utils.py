import prediction_utils as utils
import pandas as pd
from sklearn.preprocessing import StandardScaler


def build_heatmap_dev_skills_df(skills_dev_df):
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


def get_related_skills(skills_dev_df, target_jop, already_have_skills):
    heatmap_dev_skills_df = build_heatmap_dev_skills_df(skills_dev_df)
    dev_skills = heatmap_dev_skills_df.loc[target_jop, :].sort_values(ascending=False)
    related_skills = dev_skills[dev_skills > 0]
    related_skills = related_skills[~related_skills.index.isin(already_have_skills)].index
    return related_skills


def get_recommended_skills(skills_dev_df, target_jop, already_have_skills, number_recommended_skills=5):
    already_have_skills_list = already_have_skills.copy()
    features_names, target_names, model = utils.fetch_best_model_data()
    related_skills = get_related_skills(skills_dev_df, target_jop, already_have_skills_list)
    recommended_skills = []

    for i in range(number_recommended_skills):
        df = utils.prepare_df(already_have_skills_list, features_names)
        predictions = utils.predict_roles(model, df, target_names)
        base_prediction = predictions[target_jop]
        most_related_skills = {}
        for skill in related_skills:
            new_skills = already_have_skills_list + [skill]
            df = utils.prepare_df(new_skills, features_names)
            predictions = utils.predict_roles(model, df, target_names)
            skill_prediction = predictions[target_jop]

            uplift_skill_prediction = (skill_prediction - base_prediction) / base_prediction
            most_related_skills[skill] = uplift_skill_prediction
        most_related_skills = pd.Series(most_related_skills).sort_values(ascending=False)
        most_related_skill = most_related_skills.index.values[0]
        related_skills = list(related_skills)
        related_skills.remove(most_related_skill)
        already_have_skills_list += [most_related_skill]
        recommended_skills += [most_related_skill]
    # df = utils.prepare_df(already_have_skills_list, features_names)
    # predictions = utils.predict_roles(model, df, target_names)
    # new_prediction = predictions[target_jop]

    return recommended_skills


def get_all_skills(skills_dev_df):
    categories = set(skills_dev_df.drop('DevType', axis=1, level=0).columns.get_level_values(level=0))
    all_skills = list(skills_dev_df.columns)
    all_skills = [(sub[1], sub[0]) for sub in all_skills]
    all_skills = dict(all_skills)
    return all_skills, categories


def get_recommended_categories(skills_dev_df, target_jop, already_have_skills, number_recommended_skills=5):
    recommended_skills = get_recommended_skills(skills_dev_df, target_jop, already_have_skills,
                                                number_recommended_skills)

    all_skills, categories = get_all_skills(skills_dev_df)
    recommended_categories = {key: [] for key in categories}
    for skill in recommended_skills:
        skill_category = all_skills[skill]
        recommended_categories[skill_category].append(skill)

    return recommended_categories