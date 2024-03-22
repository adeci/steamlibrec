import json


def definive_library_games(library):
    return dict(sorted(library.items(), key=lambda x: x[1], reverse=True)[:25])


def load_data(file):
    with open(file, 'r', encoding='utf-8') as jf:
        return json.load(jf)


def save_data(library_data_dict, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(library_data_dict, f, indent=4)


def create_megalib(file_data):
    megalibrary = set()
    for lib in file_data.values():
        definitive_games = definive_library_games(lib)
        megalibrary.update(definitive_games.keys())
    return list(megalibrary)


def create_library_dict(file_data, megalib):
    library_dict = {}

    for lib, game_datas in file_data.items():
        definive_games = definive_library_games(game_datas)
        lib_data = {game: 0 for game in megalib}
        lib_data.update({game: definive_games.get(game, 0)
                        for game in megalib})
        library_dict[lib] = lib_data

    return library_dict


def create_weighted_dict(library_data, megalib):
    largest_play_time = {game: 0 for game in megalib}
    for lib in library_data.values():
        for game, play_time in lib.items():
            if play_time > largest_play_time[game]:
                largest_play_time[game] = play_time
    return largest_play_time


def modify_to_normalized_library_dict(library_data, megalib, weighted_dict):
    for lib in library_data.values():
        max_play_time = max(lib.values(), default=1)
        for game in megalib:
            lib[game] = lib.get(game, 0)
            if max_play_time > 0:
                lib[game] = (lib[game] / max_play_time) * 100
            if game in weighted_dict and weighted_dict[game] > 0:
                lib[game] *= (lib[game] / weighted_dict[game])
            else:
                pass


def main():
    file_data = input('Library file to load data from: ')
    file_data = '../data/' + file_data
    loaded_data = load_data(file_data)
    megalib = create_megalib(loaded_data)
    with open('../data/megalib.txt', 'w') as f:
        for game in megalib:
            f.write(game + '\n')
    print('Saved megalib for reference.')
    print('There are ' + str(len(megalib)) + ' unique games.')
    library_dict = create_library_dict(loaded_data, megalib)
    print(len(library_dict))
    weighted_dict = create_weighted_dict(library_dict, megalib)
    with open('../data/weighted_dict.json', 'w') as f:
        json.dump(weighted_dict, f, indent=4)
    modify_to_normalized_library_dict(library_dict, megalib, weighted_dict)
    file = input('Filename to save normalized library data to: ')
    save_data(library_dict, '../data/' + file)
    print('Normalized data prepared for model and saved under name:', 'data/' + file)


if __name__ == '__main__':
    main()
