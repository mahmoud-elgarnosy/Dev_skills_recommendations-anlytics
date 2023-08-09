from src.utils import MlflowUtils
import pandas as pd
from sklearn.preprocessing import StandardScaler


def fetch_best_model_data():
    run_id = MlflowUtils.get_run_id_by_metrix(metrix_name='recall')
    logged_data = MlflowUtils.fetch_logged_data(tracking_uri='../models/runs', run_id=run_id)
    features_names = logged_data['data_details']['features_names']
    target_names = logged_data['data_details']['target_names']
    model = logged_data['model']['model_object']
    return features_names, target_names, model


def prepare_df(skills, features_names):
    df = pd.DataFrame(columns=features_names)
    df.loc[0, :] = 0
    df.loc[0, skills] = 1.5
    df = df[features_names]
    return df


def predict_roles(model, df, target_names):
    predictions = model.predict_proba(df)
    positive_probs = [prob[0][1] for prob in predictions]
    return pd.Series(positive_probs,
                     index=target_names).sort_values(ascending=False)


