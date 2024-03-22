import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold
from sklearn.metrics import silhouette_score
from joblib import dump


def load_data(file):
    with open(file, 'r') as f:
        normalized_data = json.load(f)
    data_matrix = [list(lib.values()) for lib in normalized_data.values()]
    return np.array(data_matrix)


def create_data_from_ndict(norm_dict):
    data_matrix = [list(lib.values()) for lib in norm_dict.values()]
    return np.array(data_matrix)


def perform_kmeans(X, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    return kmeans


def k_fold_validation(X, n_splits=5, n_clusters=5):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    silhouette_scores = []

    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        kmeans = perform_kmeans(X_train, n_clusters=n_clusters)
        labels = kmeans.predict(X[test_index])

        if len(set(labels)) > 1:
            silhouette_avg = silhouette_score(X_test, kmeans.predict(X_test))
            silhouette_scores.append(silhouette_avg)
        else:
            print(
                "Skipped silhouette because of a single cluster calculated in this fold.")

    return np.mean(silhouette_scores) if silhouette_scores else 0


def main():
    file = input("Input data file to train model on: ")
    file = '../data/' + file
    X = load_data(file)
    n_clusters = int(input("Enter the number of clusters: "))

    avg_silhouette_score = k_fold_validation(
        X, n_splits=5, n_clusters=n_clusters)
    print(f"Average Silhouette Score across folds: {avg_silhouette_score:.2f}")

    kmeans_model = perform_kmeans(X, n_clusters=n_clusters)

    model_filename = input("Enter filename to save the trained KMeans model: ")
    model_filename = '../data/' + model_filename
    with open(model_filename, 'wb') as f:
        dump(kmeans_model, f)

    print(f"Model saved to {model_filename}")


if __name__ == '__main__':
    main()
