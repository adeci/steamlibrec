import json
import pandas as pd
import numpy as np


def load_json_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_matrix_to_csv(file, tag_time_matrix):
    df = pd.DataFrame(tag_time_matrix)
    df.to_csv(file, index=True, index_label='LibraryID')


def create_tag_time_matrix(game_tag_dict, game_playtime_dict):
    tag_time_matrix = {}
    aggregate_tags = set(tag for tags in game_tag_dict.values()
                         for tag in tags)
    print('There are', len(aggregate_tags), 'unique tags.')

    for lib_id, games_data in game_playtime_dict.items():
        id_tagtime_row = {tag: 0 for tag in aggregate_tags}

        for game, playtime in games_data.items():
            game_tag_list = game_tag_dict.get(game, [])
            if game_tag_list:
                split_n_ways_playtime = playtime / len(game_tag_list)
                for tag in game_tag_list:
                    id_tagtime_row[tag] += split_n_ways_playtime

        tag_time_matrix[lib_id] = id_tagtime_row

    return tag_time_matrix


def row_wise_normalization(tag_time_matrix):
    df = pd.DataFrame(tag_time_matrix)
    total_playtime = df.sum(axis=1)
    normalized_df = df.div(total_playtime.replace(0, np.nan), axis=0).fillna(0)
    return normalized_df.to_dict(orient='index')


def main():
    game_tag_dict = load_json_file('../data/game_tags.json')
    game_playtime_dict = load_json_file('../data/libraries.json')

    tag_time_matrix = create_tag_time_matrix(game_tag_dict, game_playtime_dict)
    normalized_tag_time_matrix = row_wise_normalization(tag_time_matrix)
    save_matrix_to_csv('../data/training_data.csv', normalized_tag_time_matrix)
    print('Saved normalized matrix to training_data.csv')


def prepare_single_data(single_library_dict):
    game_tag_dict = load_json_file('../data/game_tags.json')
    game_playtime_dict = single_library_dict

    tag_time_matrix = create_tag_time_matrix(game_tag_dict, game_playtime_dict)
    normalized_tag_time_matrix = row_wise_normalization(tag_time_matrix)
    return normalized_tag_time_matrix


if __name__ == '__main__':
    main()
