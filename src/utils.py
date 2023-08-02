import mlflow
from mlflow.tracking import MlflowClient
import pickle
import os


class MlflowUtils:
    def __init__(self, tracking_uri='../models/runs',
                 experiment_name="skills_rec_analysis",
                 artifact_temp='../models/temp'):
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self.artifact_temp = artifact_temp

        self.client, self.experiment = self.initialize_client_experiment()

    def initialize_client_experiment(self):
        # Initialize client and experiment
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        client = MlflowClient()
        experiment = client.get_experiment_by_name(self.experiment_name)
        return client, experiment

    def save_pickle_data(self, data, pkl_file='model.pkl'):
        os.makedirs(self.artifact_temp, exist_ok=True)
        with open(os.path.join(self.artifact_temp, pkl_file), "wb") as data_file:
            pickle.dump(data, data_file)

    def save_model_data(self, name, details, model_object):
        model_data = {'name': name,
                      'details': details,
                      'model_object': model_object}

        self.save_pickle_data(model_data, 'model.pkl')

    def save_matrices(self, matrices_df):
        self.save_pickle_data(matrices_df, 'matrices.pkl')

    def save_data(self, path, training_indices, testing_indices, target_names, features_names):
        data = {'path': path,
                'training_indices': training_indices,
                'testing_indices': testing_indices,
                'target_names': target_names,
                'features_names': features_names}

        self.save_pickle_data(data, 'data_details.pkl')

    def save_run_details(self, run_name, metrics):
        if not os.path.isdir(self.artifact_temp) and not os.listdir(self.artifact_temp):
            raise Exception("Sorry, There are no artifacts to save")

        # Start a new run and track
        with mlflow.start_run(experiment_id=self.experiment.experiment_id, run_name=run_name):
            # Log pickles
            mlflow.log_artifacts(self.artifact_temp)

            # Track metrics
            for metric, score in metrics.items():
                mlflow.log_metric(metric, score)

    @staticmethod
    def fetch_logged_data(tracking_uri, run_id):
        mlflow.set_tracking_uri(tracking_uri)
        run = mlflow.get_run(run_id)
        artifacts_path = run.info.artifact_uri.split('file:///')[-1]
        logged_data = {'metrics': run.data.metrics}
        for file in os.listdir(artifacts_path):
            file_path = os.path.join(artifacts_path, file)
            with open(file_path, "rb") as f:
                data_name = file.split('.')[0]
                logged_data[data_name] = pickle.load(f)

        return logged_data

    @staticmethod
    def get_runs(tracking_uri='../models/runs', experiment_name='skills_rec_analysis'):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        client = MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)
        runs = mlflow.search_runs([experiment.experiment_id])
        if runs.empty:
            raise Exception('Sorry, There are no runs for the specified experiment_id')
        else:
            return runs

    @staticmethod
    def get_run_names(tracking_uri='../models/runs', experiment_name='skills_rec_analysis'):
        runs = MlflowUtils.get_runs(experiment_name=experiment_name)
        run_names = list(runs['tags.mlflow.runName'])
        return run_names

    @staticmethod
    def get_run_id_by_run_name(run_name, experiment_name='skills_rec_analysis'):
        runs = MlflowUtils.get_runs(experiment_name=experiment_name)
        run_id = runs[runs['tags.mlflow.runName'] == run_name]['run_id']
        return run_id

    @staticmethod
    def get_run_id_by_metrix(experiment_name='skills_rec_analysis', metrix_name='precision', score='highest'):
        ascending = False if score == 'highest' else True
        runs = MlflowUtils.get_runs(experiment_name = experiment_name)
        run_id = runs.sort_values(by=f'metrics.{metrix_name}', ascending=ascending).loc[0, 'run_id']
        return run_id
