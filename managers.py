import requests
from bs4 import BeautifulSoup

# managers
managers = []


# import valid bosses by webscraping
def get_valid_managers():
    # obtain the requests for the urls
    r = requests.get('https://corporateclash.wiki.gg/wiki/Category:Managers')

    # webscrape for manager information
    if r.status_code == 200:
        # parser
        bs = BeautifulSoup(r.content, 'html.parser')

        # div
        manager_div = bs.find('div', class_='mw-category mw-category-columns')

        if manager_div:
            # identify all the manager links under the div
            links = manager_div.find_all('a', href=True)

            # parse each manager from the managers view
            counter = 0

            for link in links:
                if 'title' in link.attrs:
                    if 'href' in link.attrs:
                        # get image url
                        image_url = locate_cog_image(link['title'])

                        # create the tuple and append it
                        tuple = (counter, link['title'], str(link['title']).lower(),
                                 'https://corporateclash.wiki.gg' + str(link['href']), image_url)
                        managers.append(tuple)
                        counter += 1
            # NOTE: remove The Directors, The Litigation Team, and Unstable Cogs from the list; they aren't cog entries


def locate_cog_image(name):
    r = requests.get('https://corporateclash.wiki.gg/wiki/Employees')

    # iterate through cog names
    if r.status_code == 200:
        # parsing the content
        bs = BeautifulSoup(r.content, 'html.parser')

        sources = bs.find_all('a', title=True)

        # images
        images = {}

        # iterate through cogs
        for cog in sources:
            cog_name = cog.get('title')

            if cog_name == name:
                return 'https://corporateclash.wiki.gg' + cog.find_next('img').get('src')

        else:
            return 'https://corporateclash.wiki.gg/images/thumb/3/3a/MpCogs.png/450px-MpCogs.png'


def does_cog_exist(name):
    if name in get_id_names():
        return True


def get_cog_with_name(name):
    if not does_cog_exist(name):
        return

    for cog in managers:
        if cog[2] == name:
            return cog


def get_id_names():
    id_names = []
    for c in managers:
        id_names.append(c[2])
    return id_names


def get_cog_url(name):
    return get_cog_with_name(name)[3]


