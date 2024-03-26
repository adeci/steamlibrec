import pandas as pd
import json
from scipy.sparse import csr_matrix


def load_data(file):
    with open(file, 'r', encoding='utf-8') as jf:
        return json.load(jf)


def save_data(df, file):
    df.to_json(file, orient='index')


def prepare_data(file_data):
    df = pd.DataFrame.from_dict(file_data, orient='index').fillna(0)
    df = df.apply(lambda x: x.sort_values(
        ascending=False).head(25), axis=1).fillna(0)
    df = (df - df.min()) / (df.max() - df.min())
    df = df.fillna(0)
    return df


def prepare_single_user_library(user_library, megalib):
    user_df = pd.DataFrame.from_dict(
        user_library, orient='index', columns=['playtime']).transpose()
    user_df = user_df.apply(lambda x: x.sort_values(
        ascending=False).head(25), axis=1).fillna(0)

    missing_games = set(user_df.columns) - set(megalib)
    if missing_games:
        print("Rare case where your lib has unique games not in the model! They will be ignored for recommendations. These games are:", missing_games)

    for game in megalib:
        if game not in user_df.columns:
            user_df[game] = 0

    user_df = (user_df - user_df.min()) / (user_df.max() - user_df.min())
    user_df = user_df.fillna(0)
    user_sparse = csr_matrix(user_df.values)

    return user_sparse


def load_megalib(file):
    with open(file, 'r') as f:
        megalib = f.read().splitlines()
    return megalib


def save_megalib(megalib):
    with open('../data/megalib.txt', 'w') as f:
        for line in megalib:
            f.write(line + '\n')


def definive_library_games(library):
    return dict(sorted(library.items(), key=lambda x: x[1], reverse=True)[:25])


def create_library_dict(file_data, megalib):
    library_dict = {}

    for lib, game_datas in file_data.items():
        definive_games = definive_library_games(game_datas)
        lib_data = {game: 0 for game in megalib}
        lib_data.update({game: definive_games.get(game, 0)
                        for game in megalib})
        library_dict[lib] = lib_data

    return library_dict


def create_megalib(file_data):
    megalibrary = set()
    for lib in file_data.values():
        definitive_games = definive_library_games(lib)
        megalibrary.update(definitive_games.keys())
    return list(megalibrary)


def main_prepare_data():
    # file_data = input('Library file to load data from: ')
    file_data = '../data/libraries.json'
    loaded_data = load_data(file_data)
    megalib = create_megalib(loaded_data)
    save_megalib(megalib)
    # prepared_data = prepare_data(loaded_data)

    # save_megalib(create_megalib(load_data))

    # save_file = input('Filename to save normalized library data to: ')
    # save_data(prepared_data, '../data/' + save_file)

    # print('Normalized data prepared for model and saved under name:',
    #      'data/' + save_file)


def main_prepare_single_user(user_library):
    megalib = load_megalib('../data/megalib.txt')
    return prepare_single_user_library(user_library, megalib)


if __name__ == '__main__':
    main_prepare_data()
