import json
from joblib import load
import numpy as np
import pandas as pd
# Import the function from preparedata.py for preparing a single user's library
from preparedata import prepare_single_user_library, load_megalib


def load_model(filename):
    return load(filename)


def predict_cluster(model, user_prepared):
    # For K-means
    if hasattr(model, 'predict'):
        return model.predict(user_prepared)
    # For DBSCAN or models that use 'labels_' directly
    elif hasattr(model, 'labels_'):
        return model.labels_
    else:
        raise ValueError("Model does not support prediction.")


def recommend_games(cluster_label, model, megalib):
    if hasattr(model, 'cluster_centers_'):  # K-means
        cluster_center = model.cluster_centers_[cluster_label]
        # Indices of games sorted by cluster center proximity
        games_indices = np.argsort(cluster_center)[::-1]
    else:  # For other models, we might need a different approach
        raise NotImplementedError(
            "Recommendation for this model is not implemented.")

    recommended_games = [megalib[idx]
                         for idx in games_indices if cluster_center[idx] > 0]
    return recommended_games


def main(user_library):
    megalib = load_megalib('path_to_megalib.txt')  # Adjust path as needed
    user_prepared = prepare_single_user_library(user_library, megalib)

    model = load_model('path_to_trained_model.joblib')  # Adjust path as needed
    user_cluster = predict_cluster(model, user_prepared)

    recommended_games = recommend_games(user_cluster[0], model, megalib)
    new_game_recommendations = [
        game for game in recommended_games if game not in user_library]

    print("Recommended games not in the user's library:")
    print(new_game_recommendations)


if __name__ == '__main__':
    user_library = {
        # Example user library
        "Game A": 120,
        "Game B": 45,
        # Add more games as needed
    }
    main(user_library)
