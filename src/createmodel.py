import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import numpy as np
from kneed import KneeLocator


def load_data(file_path):
    return pd.read_csv(file_path, index_col='LibraryID')


def plot_k_distance(data, n_neighbors=5):
    nearest_neighbors = NearestNeighbors(n_neighbors=n_neighbors)
    nearest_neighbors.fit(data)
    distances, _ = nearest_neighbors.kneighbors(data)

    sorted_distances = np.sort(distances[:, n_neighbors - 1], axis=0)

    knee = KneeLocator(range(len(sorted_distances)), sorted_distances,
                       curve='convex', direction='increasing', interp_method='polynomial')

    plt.figure(figsize=(10, 5))
    plt.plot(sorted_distances)
    plt.xlabel(
        "Points sorted by distance to the {}-th nearest neighbor".format(n_neighbors))
    plt.ylabel("{}-th nearest neighbor distance".format(n_neighbors))
    plt.title("K-distance Graph for Tuning EPS in DBSCAN")
    plt.grid(True)
    plt.locator_params(axis='y', nbins=20)
    plt.annotate('Elbow', xy=(knee.knee, knee.knee_y), xytext=(
        knee.knee, knee.knee_y), arrowprops=dict(facecolor='red', shrink=0.05))

    plt.savefig('../data/k_distance_graph.png')
    plt.close()

    print(
        f"Estimated 'elbow' point at index: {knee.knee}, with an 'eps' value of: {knee.knee_y:.3f}")


def train_dbscan(data, eps=0.5, min_samples=5):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dbscan.fit(data)
    return dbscan.labels_


def evaluate_clusters(data, labels):
    data['Cluster'] = labels
    unique_clusters = set(labels)

    noise_points = sum(labels == -1)

    print(f"Number of clusters formed: {len(unique_clusters) - 1}")
    print(f"Number of data points considered as noise: {noise_points}")

    for cluster in unique_clusters:
        if cluster == -1:
            continue
        print(f"\nCluster {cluster}:")
        cluster_data = data[data['Cluster'] == cluster].drop('Cluster', axis=1)

        tag_means = cluster_data.mean(axis=0).sort_values(ascending=False)

        print(tag_means.head(5))

    data.to_csv('../data/labelled_data.csv', index=True)
    print('Saved the labelled data for classifier training to labelled_data.csv')


def main():
    data = load_data('../data/training_data.csv')

    sample_num = 2

    plot_k_distance(data, n_neighbors=sample_num)

    chosen_eps = float(
        input("Enter the chosen 'eps' value based on the k-distance plot: "))
    min_samples = sample_num

    dbscan_labels = train_dbscan(data, eps=chosen_eps, min_samples=min_samples)
    evaluate_clusters(data, dbscan_labels)


if __name__ == '__main__':
    main()
