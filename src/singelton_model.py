from notebooks.prediction_utils import fetch_best_model_data


class ModelLoaderSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoaderSingleton, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        self.features_names, self.target_names, self.model = fetch_best_model_data()


# Usage:
if __name__ == "__main__":
    loader1 = ModelLoaderSingleton()
    model1 = loader1.model
    print(loader1.features_names)

    loader2 = ModelLoaderSingleton()
    model2 = loader2.model

    print(model2)
    assert model1 is model2

    # loader1 and loader2 are the same instance, and data_frame1 and data_frame2 contain the loaded data.
