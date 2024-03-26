import json
import pandas as pd
from scipy.sparse import load_npz
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from matplotlib import pyplot as plt
from joblib import dump
from sklearn.neighbors import NearestNeighbors
import numpy as np


def plot_k_distance_graph(X, k):
    nbrs = NearestNeighbors(n_neighbors=k).fit(X)
    distances, indices = nbrs.kneighbors(X)

    sorted_distances = np.sort(distances[:, k-1], axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(sorted_distances)
    plt.title(f'k-distance Graph (k={k})')
    plt.xlabel('Points sorted by distance')
    plt.ylabel(f'Distance to {k}-th nearest neighbor')
    plt.grid(True)
    plt.savefig('../models/distance_graph.png')
    plt.close()


def apply_pca(X, n_components=0.95):
    pca = PCA(n_components=n_components, svd_solver='full')
    X_reduced = pca.fit_transform(X)
    print(f"Reduced feature space to {X_reduced.shape[1]} dimensions")
    return X_reduced


def load_data(file):
    try:
        data_matrix = load_npz(file)
    except ValueError:
        with open(file, 'r') as f:
            normalized_data = json.load(f)
        data_matrix = pd.DataFrame.from_dict(
            normalized_data, orient='index').to_numpy()
    return data_matrix


def elbow_method(X, range_n_clusters=[2, 3, 4, 5, 6, 7, 8, 9, 10]):
    sse = []
    for n_clusters in range_n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        sse.append(kmeans.inertia_)

    plt.figure(figsize=(10, 6))
    plt.plot(range_n_clusters, sse, marker='o')
    plt.title('Elbow Method For Optimal k')
    plt.xlabel('Number of clusters')
    plt.ylabel('Sum of squared distances')
    plt.savefig('../models/elbow.png')
    plt.close()


def silhouette_evaluation(X, cluster_labels):
    silhouette_avg = silhouette_score(X, cluster_labels)
    print(f"Silhouette Score: {silhouette_avg:.2f}")


def perform_kmeans(X, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)
    return kmeans


def perform_dbscan(X, eps=0.5, min_samples=5):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dbscan.fit(X)
    return dbscan


def main():
    file = input("Input data file to train model on: ")
    file = '../data/' + file
    X_original = load_data(file)

    X = apply_pca(X_original)

    elbow_method(X)
    plot_k_distance_graph(X, 25)

    n_clusters = int(input("Enter the number of clusters for KMeans: "))
    kmeans_model = perform_kmeans(X, n_clusters=n_clusters)
    silhouette_evaluation(X, kmeans_model.labels_)

    kmeans_model_filename = '../models/kmeans'
    with open(kmeans_model_filename, 'wb') as f:
        dump(kmeans_model, f)
    print(f"KMeans Model saved to {kmeans_model_filename}")

    eps = float(input("Enter epsilon for DBSCAN: "))
    min_samples = int(input("Enter min_samples for DBSCAN: "))
    dbscan_model = perform_dbscan(X, eps=eps, min_samples=min_samples)

    silhouette_evaluation(X, dbscan_model.labels_)

    dbscan_model_filename = '../models/dbscan'
    with open(dbscan_model_filename, 'wb') as f:
        dump(dbscan_model, f)
    print(f"DBSCAN Model saved to {dbscan_model_filename}")


if __name__ == '__main__':
    main()
