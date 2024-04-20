import json
from getlibraries import single_library_fetch
import pandas as pd


def fetch_library_ids_by_cluster(cluster_number, cluster_label_file):
    # Load the merged cluster labels CSV
    cluster_df = pd.read_csv(cluster_label_file)
    # Filter to get library IDs where MergedCluster equals the specified cluster_number
    libraries_in_cluster = cluster_df[cluster_df['MergedCluster']
                                      == cluster_number]['LibraryID'].tolist()
    return libraries_in_cluster


def get_libraries_games(library_ids, library_file):
    # Load the complete libraries JSON
    all_libraries = load_json(library_file)
    # Filter to get only the libraries that match the IDs
    libraries_games = {lib_id: all_libraries.get(
        str(lib_id), {}) for lib_id in library_ids}
    return libraries_games


def find_top_games(libraries_games, user_games):
    game_playtimes = {}
    # Aggregate playtimes for each game across all provided libraries, excluding user's games
    for games in libraries_games.values():
        for game, playtime in games.items():
            if game not in user_games:  # Check if the game is not in the user's library
                if game in game_playtimes:
                    game_playtimes[game] += playtime
                else:
                    game_playtimes[game] = playtime

    # Sort games by total playtime and select the top 3
    top_games = sorted(game_playtimes.items(),
                       key=lambda x: x[1], reverse=True)[:3]
    return top_games


def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def calculate_similarity_scores(user_tags, cluster_tags):
    user_tag_set = set(user_tags)
    scores = {}
    for cluster_id, tags in cluster_tags.items():
        cluster_tag_set = set(tags)
        intersection = user_tag_set.intersection(cluster_tag_set)
        union = user_tag_set.union(cluster_tag_set)
        jaccard_index = len(intersection) / len(union) if union else 0
        scores[cluster_id] = jaccard_index
    return scores


def normalize_scores(scores):
    total_score = sum(scores.values())
    normalized_scores = {k: v / total_score for k,
                         v in scores.items() if total_score > 0}
    return normalized_scores


def assign_clusters(user_tags, cluster_file):
    cluster_tags = load_json(cluster_file)
    scores = calculate_similarity_scores(user_tags, cluster_tags)
    normalized_scores = normalize_scores(scores)
    return normalized_scores


def get_top_tags_by_playtime(game_playtimes, game_tags, blacklist=[]):
    tag_playtimes = {}
    blacklist_set = set(blacklist)

    # Aggregate playtime for each tag, excluding blacklisted tags
    for game, playtime in game_playtimes.items():
        tags = game_tags.get(game, [])
        for tag in tags:
            if tag not in blacklist_set:
                if tag in tag_playtimes:
                    tag_playtimes[tag] += playtime
                else:
                    tag_playtimes[tag] = playtime

    # Sort tags by total playtime and get the top 10
    sorted_tags = sorted(tag_playtimes.items(),
                         key=lambda x: x[1], reverse=True)
    top_tags = sorted_tags[:10]

    return top_tags


def main():
    steamid = input('Input steamid for user: ')
    userlib, all_lib = single_library_fetch(steamid)
    game_playtimes = userlib[next(iter(userlib))]
    user_games = set(all_lib.keys())
    # get the tag dictionary file
    game_tags = load_json('../data/game_tags.json')

    # Define a list of tags to exclude
    blacklist = ['Free to Play', 'Multiplayer',
                 'Early Access', 'Action', 'RPG', 'Adventure',
                 'Indie', 'Strategy', 'Open World',
                 'Simulation', 'Singleplayer', 'Casual', 'FPS']

    top_tags = get_top_tags_by_playtime(game_playtimes, game_tags, blacklist)
    print(top_tags)
    # Example usage
    cluster_percentages = assign_clusters(
        [tag for tag, _ in top_tags], '../data/merged_clusters.json')

    # Print the results
    top_clusters = []
    games = set()
    for cluster_id, percentage in sorted(cluster_percentages.items(), key=lambda x: x[1], reverse=True):
        print(f"Cluster {cluster_id}: {percentage:.2%} similarity")
        if float(percentage * 100) > 10.00:
            top_clusters.append(cluster_id)
    print("Based on your preferences and similarity alignment you are most likely to enjoy in order:")
    for cluster_number in top_clusters:
        library_ids = fetch_library_ids_by_cluster(
            int(cluster_number), '../data/merged_dbscan_cluster_labels.csv')
        libraries_games = get_libraries_games(
            library_ids, '../data/libraries.json')
        top_games = find_top_games(libraries_games, user_games)
        for game, playtime in top_games:
            if game not in games:
                games.add(game)
                print(f'{game}')


if __name__ == '__main__':
    main()
