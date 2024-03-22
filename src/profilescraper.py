import requests
from bs4 import BeautifulSoup


def get_group_profiles(group, goal):
    id_list = []
    page_num = 1

    while len(id_list) < goal:
        print("Now scraping page " + str(page_num))
        group_url = group + "/members/?p=" + str(page_num)
        response = requests.get(group_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            members = soup.find_all('div', class_='playerAvatar')

            for member in members:
                if len(id_list) < goal:
                    profile = member.find('a', href=True)
                    if profile:
                        url = profile['href']
                        id = url.split('/')[-1]
                        id_list.append(id)
                else:
                    break

            page_num += 1

        else:
            print("Scraping failed on page", page_num,
                  "with error code", response.status_code)
            break

    return id_list


def main():
    groupurl = input("Input group URL: ")
    num = int(input("How many member ids to fetch: "))
    ids = get_group_profiles(groupurl, num)
    print('Fetched', str(len(ids)), 'unique profile IDs.')
    filename = input('Filename to save group IDs to: ')
    filename = '../data/' + filename
    with open(filename, 'w') as f:
        for id in ids:
            f.write(id + '\n')


if __name__ == '__main__':
    main()
