import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from kneed import KneeLocator


def load_data(file_path):
    return pd.read_csv(file_path, index_col='LibraryID')


def find_optimal_eps(data, plot_path):
    neigh = NearestNeighbors(n_neighbors=4)
    nbrs = neigh.fit(data)
    distances, indices = nbrs.kneighbors(data)

    distances = np.sort(distances, axis=0)[:, 3]
    kneedle = KneeLocator(range(len(distances)), distances, curve='convex',
                          direction='increasing', interp_method='polynomial')

    # Plot the knee
    plt.figure(figsize=(8, 4))
    kneedle.plot_knee()
    plt.xlabel('Points sorted by distance')
    plt.ylabel('Distance')
    plt.savefig(plot_path)
    plt.close()

    return kneedle.elbow, kneedle.elbow_y


def apply_dbscan(data, eps, min_samples):
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(data)
    labels = db.labels_
    cluster_df = pd.DataFrame({'Cluster': labels}, index=data.index)
    cluster_df.to_csv('../data/dbscan_cluster_labels.csv')

    return labels


def list_top_tags_per_cluster(data, labels):
    # Remove noise labels
    clusters = [label for label in set(labels) if label >= 0]
    top_tags = {}

    for cluster in clusters:
        cluster_data = data[labels == cluster]
        mean_values = cluster_data.mean(axis=0).sort_values(ascending=False)
        top_tags[cluster] = mean_values.head(3).index.tolist()

    return top_tags


def merge_clusters_by_tags(cluster_tags, threshold=0.5):
    merge_map = {}
    unique_clusters = list(cluster_tags.keys())
    new_cluster_id = 0
    cluster_id_map = {}
    new_cluster_tags = {}

    for i, cluster_i in enumerate(unique_clusters[:-1]):
        if cluster_i in merge_map:
            continue
        for cluster_j in unique_clusters[i+1:]:
            if cluster_j in merge_map:
                continue
            tags_i = set(cluster_tags[cluster_i])
            tags_j = set(cluster_tags[cluster_j])
            intersection = tags_i.intersection(tags_j)
            union = tags_i.union(tags_j)
            similarity = len(intersection) / len(union)
            if similarity >= threshold:
                merge_map[cluster_j] = cluster_i

    # Assign new cluster IDs and merge tags
    for cluster in unique_clusters:
        if cluster not in merge_map:
            new_cluster_tags[new_cluster_id] = cluster_tags[cluster]
            cluster_id_map[cluster] = new_cluster_id
            new_cluster_id += 1
        else:
            original_cluster = merge_map[cluster]
            cluster_id_map[cluster] = cluster_id_map[original_cluster]

    return new_cluster_tags, cluster_id_map


def save_merged_clusters(cluster_tags, filename):
    cluster_tags_str = {str(k): v for k, v in cluster_tags.items()}
    with open(filename, 'w') as f:
        json.dump(cluster_tags_str, f)


def main():
    data = load_data('../data/scaled_tag_time_matrix_excluded.csv')
    eps, eps_y = find_optimal_eps(data, '../models/eps_plot.png')
    new_eps = input('Input eps to use, or blank for auto-calculated value: ')
    if new_eps == '':
        new_eps = eps_y
    min_samples = 3
    labels = apply_dbscan(data, float(new_eps), min_samples)
    top_tags = list_top_tags_per_cluster(data, labels)
    merged_tags, cluster_id_map = merge_clusters_by_tags(
        top_tags, threshold=0.5)

    # Update the cluster labels with merged IDs
    cluster_df = pd.read_csv('../data/dbscan_cluster_labels.csv')
    cluster_df['MergedCluster'] = cluster_df['Cluster'].map(cluster_id_map)
    cluster_df.to_csv('../data/merged_dbscan_cluster_labels.csv', index=False)
    print("Updated cluster labels with merged IDs saved to 'merged_dbscan_cluster_labels.csv'.")

    for cluster, tags in merged_tags.items():
        print(f"Merged Cluster {cluster}: Top tags: {tags}")

    # Save the merged cluster tags to a JSON file
    save_merged_clusters(merged_tags, '../data/merged_clusters.json')
    print("Merged cluster tags saved to 'merged_clusters.json'.")


if __name__ == '__main__':
    main()
