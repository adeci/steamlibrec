import joblib
import numpy as np
import json

# Custom imports
import preparedata
import libraryfetch
import createmodel


def load_model(file):
    return joblib.load(file)


def recommendations(centroid, vector, megalib):
    distances = np.linalg.norm(centroid - vector, axis=1)
    idxs = np.argsort(distances)[:5]
    return [megalib[i] for i in idxs if vector[0, i] == 0]


def main():
    model = load_model('../data/model')

    megalib_file = '../data/megalib.txt'
    megalib = []
    with open(megalib_file, 'r') as f:
        for line in f:
            game = line.strip()
            megalib.append(game)

    weighted_dict_file = '../data/weighted_dict.json'
    weighted_dict = {}
    with open(weighted_dict_file, 'r', encoding='utf-8') as jf:
        weighted_dict = json.load(jf)

    steamid = input('Input your steamID: ')
    lib = libraryfetch.get_single_library(steamid)
    if lib is False:
        print('Failed to get your library data! Is your information public?')
        return

    your_lib = {}
    your_lib[steamid] = lib

    lib_dict = preparedata.create_library_dict(your_lib, megalib)
    print('Library transposed to megalib successfully')

    preparedata.modify_to_normalized_library_dict(
        lib_dict, megalib, weighted_dict)
    print('Library was normalized successfully')

    input_data = createmodel.create_data_from_ndict(lib_dict)

    cluster = model.predict(input_data)
    centroid = model.cluster_centers_[cluster[0]]

    recs = recommendations(centroid, input_data, megalib)
    print("Your customized game recommendations:")
    for game in recs:
        print(game)


if __name__ == '__main__':
    main()
