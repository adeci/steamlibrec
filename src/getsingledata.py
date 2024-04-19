import getlibraries
import createinput
import pandas as pd
from joblib import load


def get_single_data(steamid):
    user_library = getlibraries.single_library_fetch(steamid)
    normalized_data = createinput.prepare_single_data(user_library)
    ready_data = pd.DataFrame([normalized_data], columns=training_columns)
    return ready_data


def main():
    steamid = input('Input your steam ID: ')
    data = get_single_data(steamid)
    classifier = load('../data/classifier.joblib')
    prediction = classifier.predict(data)
    print('Your grouping is in cluster: ' + str(prediction[0]))


if __name__ == '__main__':
    main()
