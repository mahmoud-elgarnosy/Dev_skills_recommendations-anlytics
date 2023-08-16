import pandas as pd
import numpy as np
import sklearn.metrics as skm
import sklearn.preprocessing as skp
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from src.utils import MlflowUtils


def confusion_matrix_scores(confusion_matrix):
    # tp / tp + fn
    recall = confusion_matrix[1, 1] / (confusion_matrix[1, 1] + confusion_matrix[1, 0])
    accuracy = (confusion_matrix[1, 1] + confusion_matrix[0, 0]) / confusion_matrix.sum().sum()

    if not (confusion_matrix[1, 1] + confusion_matrix[0, 1]):
        precision = 0.0
    else:
        precision = confusion_matrix[1, 1] / (confusion_matrix[1, 1] + confusion_matrix[0, 1])

    if recall and precision:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {'precision': precision, 'recall': recall, 'f1_score': f1, 'accuracy': accuracy}


class ModelingUtils:
    def __init__(self, skills_dev_df, pipline_model):
        self.skills_dev_df_cp = skills_dev_df
        self.X_train, self.Y_train = None, None
        self.X_test, self.Y_test = None, None
        self.sample_weights = None
        self.job_names = None
        self.pipline_model = pipline_model

        self.split_data()
        self.calculate_sample_weights()

    def split_data(self):
        msk = np.random.rand(len(self.skills_dev_df_cp)) < 0.8
        train_df, test_df = self.skills_dev_df_cp[msk], self.skills_dev_df_cp[~msk]

        def x_y_split(df):
            X = df.drop('DevType', axis=1, level=0).droplevel(axis=1, level=0)
            Y = df['DevType']
            return X, Y

        self.X_train, self.Y_train = x_y_split(train_df)
        self.X_test, self.Y_test = x_y_split(test_df)

    def calculate_sample_weights(self):
        jobs_freq = self.Y_train.sum().reset_index()
        jobs_freq.columns = ['job_type', 'freq']
        jobs_freq.loc[:, 'class_weights'] = jobs_freq['freq'].sum() / (
                jobs_freq['job_type'].count() * jobs_freq['freq'])

        sample_weights = (jobs_freq['class_weights'].values * self.Y_train.values).sum(axis=1)
        self.sample_weights = pd.Series(sample_weights, index=self.Y_train.index, name='weights')
        self.job_names = jobs_freq['job_type'].values

    def train_evaluate_model_features(self):
        all_classification_report = []
        self.pipline_model.fit(self.X_train, self.Y_train, multioutputclassifier__sample_weight=self.sample_weights)
        for j, evaluate_type in enumerate(['train', 'test']):
            classification_report = {}
            f1_scores = []
            if j:
                X, Y = self.X_test, self.Y_test
            else:
                X, Y = self.X_train, self.Y_train

            multilabel_confusion_matrices = skm.multilabel_confusion_matrix(Y, self.pipline_model.predict(X))
            for n, cm in enumerate(multilabel_confusion_matrices):
                results = confusion_matrix_scores(cm)
                classification_report[self.job_names[n]] = results
                f1_scores.append(results['f1_score'])

            print(evaluate_type + '_f1-score: ', np.array(f1_scores).mean())
            classification_report = pd.DataFrame(classification_report).T

            classification_report.columns = pd.MultiIndex.from_product(
                [[evaluate_type], classification_report.columns])
            if isinstance(all_classification_report, pd.DataFrame):
                all_classification_report = all_classification_report.merge(classification_report, left_index=True,
                                                                            right_index=True)
            else:
                all_classification_report = classification_report.copy()

        return self.pipline_model, all_classification_report


    def save_results(self, data_path):
        mlflow_utils_original_features = MlflowUtils(artifact_temp='../models/temp/basic_model_original_features')
        mlflow_utils_original_features.save_data(path=data_path,
                                                 training_indices=self.X_train.index,
                                                 testing_indices=self.X_test.index,
                                                 target_names=self.job_names,
                                                 features_names=original_features)

        mlflow_utils_original_features.save_model_data(name='basic_model_original_features',
                                                       details=str(original_features_model),
                                                       model_object=original_features_model)

        mlflow_utils_original_features.save_matrices(classification_report_original_features)

        original_features_metrics = classification_report_original_features['original_features-test'].loc['Mean', :]
        original_features_metrics = pd.Series(original_features_metrics).to_dict()
        mlflow_utils_original_features.save_run_details('1.basic_model_with_original_features',
                                                        metrics=original_features_metrics)
