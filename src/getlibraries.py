import requests
from decouple import config
import time
from tqdm import tqdm
import json

API_KEY = config('STEAM_API_KEY')


def test_valid_connection():
    try:
        requests.get('https://www.google.com/', timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def attempt_request(api_call_url, parameters):
    while True:
        try:
            response = requests.get(api_call_url, params=parameters)
            return response
        except (requests.ConnectionError):
            print('Lost connection. Reconnecting!')
            while not test_valid_connection():
                print('Cannot reconnect yet. Waiting a moment.')
                time.sleep(10)
            print("Valid connection re-established!")


def check_hidden_playtime(library):
    for playtime in library.values():
        if int(playtime) != 0:
            return False
    return True


def check_id_validity(steamid):
    if not steamid.isdigit() or len(steamid) != 17 or not steamid.startswith('7656'):
        return False
    return True


def get_steamid_from_customid(custom_profile_name):
    api_call_url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'

    parameters = {
        'key': API_KEY,
        'vanityurl': custom_profile_name
    }

    response = attempt_request(api_call_url, parameters)
    data = response.json()

    if 'response' in data and 'success' in data['response'] and data['response']['success'] == 1:
        steamid = data['response'].get('steamid', None)
        return steamid
    else:
        tqdm.write('Failed to get steamid from custom url')
        return None


def public_check(steamid):

    api_call_url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'

    parameters = {
        'key': API_KEY,
        'steamids': steamid,
        'format': 'json'
    }

    response = attempt_request(api_call_url, parameters)

    if response.status_code == 200:
        data = response.json()

        if 'response' in data and 'players' in data['response'] and data['response']['players']:
            visibility = data['response']['players'][0].get(
                'communityvisibilitystate', 0)
            return visibility == 3
        else:
            tqdm.write('No data found for user with steamID ' + steamid)
            return False
    else:
        tqdm.write('Failed to get data for profile with steamID ' + steamid)
        return False


def get_library(steamid, aggregate_game_appid_dict, request_times):
    library = {}

    if not check_id_validity(steamid):
        steamid = get_steamid_from_customid(steamid)
        request_times.append(time.time())

    request_times.append(time.time())
    if public_check(steamid):
        api_call_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'

        parameters = {
            'key': API_KEY,
            'steamid': steamid,
            'include_appinfo': 'true',
            'include_played_free_games': 'true',
            'format': 'json'
        }

        response = attempt_request(api_call_url, parameters)
        request_times.append(time.time())

        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'games' in data['response']:
                library = {game.get('name'): game.get('playtime_forever', 0)
                           for game in data['response']['games']}

            if check_hidden_playtime(library):
                tqdm.write('Failed to fetch library for ' + steamid)
                return False, steamid

            tqdm.write('Successfully fetched library for ' + steamid)
            refined_library = keep_top_ten_games(library)

            appids = {game.get('name'): game.get('appid', 0)
                      for game in data['response']['games']}
            for game, appid in appids.items():
                if game in refined_library:
                    aggregate_game_appid_dict[game] = appid

            return refined_library, steamid

        else:
            tqdm.write(
                'Failed to get data for profile library with steamid ' + steamid + ' this should not happen with public check!')
            return False, steamid
    else:
        tqdm.write('Profile is not public!')
        return False, steamid


def keep_top_ten_games(library):
    sorted_by_playtime = sorted(
        library.items(), key=lambda x: x[1], reverse=True)
    refined_library = dict(sorted_by_playtime[:10])
    return refined_library


def main():
    filename = input('Input a group id list file: ')
    filename = '../data/' + filename
    ids = []
    with open(filename, 'r') as f:
        for line in f:
            steamid = line.strip()
            if len(steamid) > 0:
                ids.append(steamid)
    libraries_dict = {}
    request_times = []
    aggregate_game_appid_dict = {}

    for id in tqdm(ids, desc='Fetch Progress', position=0):

        time_now = time.time()
        request_times = [
            request_time for request_time in request_times if time_now - request_time < 60]

        if len(request_times) >= 65:
            with tqdm(total=60, desc="API Call Cooldown", leave=False, position=1) as pbar:
                for i in range(60):
                    time.sleep(1)
                    pbar.update(1)
            request_times = []

        lib, id = get_library(id, aggregate_game_appid_dict, request_times)
        if lib:
            libraries_dict[id] = lib

    print('Fetched', str(len(libraries_dict)), 'total libraries')
    success_rate = (len(libraries_dict) / len(ids)) * 100
    print('Success rate: {}/{} = {:.2f}%'.format(len(libraries_dict),
          len(ids), success_rate))
    file = 'libraries.json'
    with open('../data/' + file, 'w', encoding='utf-8') as f:
        json.dump(libraries_dict, f, indent=4)
    print('Completed writing libraries to file:', file)

    with open('../data/game_ids.json', 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(aggregate_game_appid_dict.items())), f, indent=4)
    print('Saved complete game to appid dictionary to file game_ids.json')


if __name__ == '__main__':
    main()
