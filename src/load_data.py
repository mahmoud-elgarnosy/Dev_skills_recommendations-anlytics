import os
import pandas as pd
import pickle


class DataLoaderSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoaderSingleton, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        LOAD_PATH = '../data/interim/'
        LOAD_PATH = os.path.join(script_dir, LOAD_PATH)
        LOAD_SKILLS_DEV_CSV = '7.0-Chosen_features_and_roles.csv'

        # Use os.path.join to combine the directory path and filename
        csv_file_path = os.path.join(LOAD_PATH, LOAD_SKILLS_DEV_CSV)

        self.skills_dev_df = pd.read_csv(csv_file_path, header=[0, 1], skipinitialspace=True, index_col=[0])
        self.skills_dev_df.columns = pd.MultiIndex.from_tuples(self.skills_dev_df.columns)


# Usage:
if __name__ == "__main__":
    loader1 = DataLoaderSingleton()
    data_frame1 = loader1.skills_dev_df

    loader2 = DataLoaderSingleton()
    data_frame2 = loader2.skills_dev_df

    assert data_frame2 is data_frame1

    # loader1 and loader2 are the same instance, and data_frame1 and data_frame2 contain the loaded data.
