import json
import pandas as pd


def load_json_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_matrix_to_csv(file, data):
    df = pd.DataFrame(data)
    df.to_csv(file, index=True, index_label='LibraryID')


def create_tag_time_matrix(game_tag_dict, game_playtime_dict, exclude_tags):
    tag_time_matrix = {}
    aggregate_tags = set(tag for tags in game_tag_dict.values()
                         for tag in tags if tag not in exclude_tags)
    print('There are', len(aggregate_tags), 'unique tags after exclusion.')

    for lib_id, games_data in game_playtime_dict.items():
        id_tagtime_row = {tag: 0 for tag in aggregate_tags}
        for game, playtime in games_data.items():
            game_tag_list = [tag for tag in game_tag_dict.get(
                game, []) if tag in aggregate_tags]
            if game_tag_list:
                split_n_ways_playtime = playtime / len(game_tag_list)
                for tag in game_tag_list:
                    id_tagtime_row[tag] += split_n_ways_playtime

        tag_time_matrix[lib_id] = id_tagtime_row

    return tag_time_matrix


def max_scale_normalization(tag_time_matrix):
    df = pd.DataFrame(tag_time_matrix).transpose()
    max_values = df.max(axis=1)
    scaled_df = df.div(max_values, axis=0)
    return scaled_df


def main():
    game_tag_dict = load_json_file('../data/game_tags.json')
    game_playtime_dict = load_json_file('../data/libraries.json')
    exclude_tags = ['Action', 'RPG', 'Adventure',
                    'Indie', 'Strategy', 'Open World',
                    'Simulation', 'Singleplayer', 'Casual',
                    'FPS']

    tag_time_matrix = create_tag_time_matrix(
        game_tag_dict, game_playtime_dict, exclude_tags)
    scaled_df = max_scale_normalization(tag_time_matrix)

    save_matrix_to_csv(
        '../data/scaled_tag_time_matrix_excluded.csv', scaled_df)
    print('Saved scaled tag-time matrix (with exclusions) to scaled_tag_time_matrix_excluded.csv')


if __name__ == '__main__':
    main()
