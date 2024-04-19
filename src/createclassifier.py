from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
import pandas as pd
from joblib import dump


def train_optimal_classifier(data):
    training_data = data[data['Cluster'] != -1]
    training_labels = training_data['Cluster']
    training_features = training_data.drop('Cluster', axis=1)

    knn = KNeighborsClassifier()
    stratified_k_fold = StratifiedKFold(n_splits=5)
    hyperparamters = {'n_neighbors': [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]}

    grid_search = GridSearchCV(
        knn, hyperparamters, cv=stratified_k_fold, scoring='accuracy')
    grid_search.fit(training_features, training_labels)

    best_model = grid_search.best_estimator_

    print('The best K was:', grid_search.best_params_['n_neighbors'])

    return best_model


def create_model():
    labeled_data = pd.read_csv(
        '../data/labelled_data.csv', index_col='LibraryID')

    classifier = train_optimal_classifier(labeled_data)
    return classifier


def main():
    best_model = create_model()
    dump(best_model, '../data/classifier.joblib')


if __name__ == '__main__':
    main()
