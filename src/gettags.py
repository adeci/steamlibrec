import json
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import matplotlib.pyplot as plt


def load_game_appid_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def scrape_tags_from_appid(appid):
    site = 'https://store.steampowered.com/app/' + appid
    response = requests.get(site)
    if response.status_code == 200 and response.content:
        soup = BeautifulSoup(response.content, 'html.parser')
        tags_container = soup.find('div', class_='glance_tags popular_tags')
        tags = tags_container.find_all('a', class_='app_tag', limit=5)
        tags_text = [tag.get_text(strip=True) for tag in tags]
    else:
        tqdm.write('Failed to get reply. Waiting 10s and trying again.')
        time.sleep(10)
        tags_text = scrape_tags_from_appid(appid)
    return tags_text


def get_game_tag_dict(game_appid_dict):
    game_tag_dict = {}
    for game, appid in tqdm(game_appid_dict.items(), desc='Tag Fetch Progress', position=0):
        tags = scrape_tags_from_appid(str(appid))
        game_tag_dict[game] = tags

        tqdm.write('Got [' + ', '.join(tags) + '] tags for ' + game)
        time.sleep(5)
    return game_tag_dict


def get_frequency_dict(game_tag_dict):
    tag_freq_dict = {}
    for tags in game_tag_dict.values():
        for tag in tags:
            if tag in tag_freq_dict:
                tag_freq_dict[tag] += 1
            else:
                tag_freq_dict[tag] = 1
    return tag_freq_dict


def clean_tag_freq_dict(tag_freq_dict):
    print('Generating histogram...')
    print('Minimum frequency observed is', min(tag_freq_dict.values()))
    print('Maximum frequency observed is', max(tag_freq_dict.values()))
    bin_num = int(input('Histogram number of bins desired: '))

    values = list(tag_freq_dict.values())
    plt.hist(values, bins=bin_num)
    plt.xlabel('Occurrence Count')
    plt.ylabel('Number of Tags')
    plt.title('Distribution of Tag Occurrences')
    plt.savefig('../data/tag_distribution.png')
    plt.close()

    threshold = int(input('Review histogram and input threshold for cutoff: '))

    clean_dict = {}
    removed_list = []
    for tag, freq in tag_freq_dict.items():
        if freq >= threshold:
            clean_dict[tag] = freq
        else:
            removed_list.append(tag)

    print(len(removed_list), 'tags filteres out:', removed_list)
    print('There are now', len(clean_dict),
          'tags to be used out of the original', len(tag_freq_dict))

    return clean_dict


def filter_game_tag_dict(game_tag_dict, cleaned_tag_freq_dict):
    filtered_game_tag_dict = {}
    for game, tags in game_tag_dict.items():
        filtered_tags = [tag for tag in tags if tag in cleaned_tag_freq_dict]
        filtered_game_tag_dict[game] = filtered_tags[:3]
    return filtered_game_tag_dict


def main():
    game_appid_dict = load_game_appid_data('../data/game_ids.json')
    game_tag_dict = get_game_tag_dict(game_appid_dict)
    tag_freq_dict = get_frequency_dict(game_tag_dict)
    cleaned_tag_freq_dict = clean_tag_freq_dict(tag_freq_dict)
    filtered_game_tag_dict = filter_game_tag_dict(
        game_tag_dict, cleaned_tag_freq_dict)

    with open('../data/game_tags.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_game_tag_dict, f)
    print('Saved the filtered game tag dictionary to game_tags.json')

    with open('../data/tag_freqs.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_tag_freq_dict, f)
    print('Saved the tag frequencies for insights to tag_freqs.json')


if __name__ == '__main__':
    main()
