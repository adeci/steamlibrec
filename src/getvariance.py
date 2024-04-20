import pandas as pd
import matplotlib.pyplot as plt


def load_data(file_path):
    return pd.read_csv(file_path, index_col='LibraryID')


def plot_tag_variance(data):
    # Calculate variance for each tag
    tag_variance = data.var().sort_values(ascending=False)

    # Plotting the variances
    plt.figure(figsize=(12, 8))
    tag_variance.plot(kind='bar')
    plt.title('Variance of Each Tag')
    plt.xlabel('Tags')
    plt.ylabel('Variance')
    plt.xticks(rotation=90)  # Rotate labels for better readability
    plt.tight_layout()
    plt.savefig('../data/tag_variance.png')
    plt.show()


def main():
    data = load_data('../data/scaled_tag_time_matrix_excluded.csv')
    plot_tag_variance(data)


if __name__ == '__main__':
    main()
