import requests
from bs4 import BeautifulSoup

# cogs
cogs = []


# format of cog tuples: id, name, id_name, wiki_url, image_url
# define the valid cog names
def get_valid_cogs():
    # get request for url
    r = requests.get('https://corporateclash.wiki.gg/wiki/Category:Employees')
    r2 = requests.get('https://corporateclash.wiki.gg/wiki/Category:Field_Specialists')
    r3 = requests.get('https://corporateclash.wiki.gg/wiki/Category:Operations_Analysts')

    # SPAGHETTI CODE!!!!!!! (im just too lazy to fix this)

    # iterate through vanilla cog names
    if r.status_code == 200:
        # parsing the content
        bs = BeautifulSoup(r.content, 'html.parser')

        # setting up the view
        cog_div = bs.find('div', class_='mw-category mw-category-columns')

        # getting the names
        if cog_div:
            # obtain link
            links = cog_div.find_all('a', href=True)
            counter = 0

            for link in links:
                if 'title' in link.attrs:
                    if 'href' in link.attrs:
                        # get image url
                        image_url = locate_cog_image(link['title'])

                        # create the tuple and append it
                        tuple = (counter, link['title'], str(link['title']).lower(), 'https://corporateclash.wiki.gg' + str(link['href']), image_url)
                        cogs.append(tuple)
                        counter += 1

    # iterate through field specialist cog names
    if r2.status_code == 200:
        # parsing the content
        bs = BeautifulSoup(r2.content, 'html.parser')

        # getting the ul elements of the page
        # links = bs.find_all('a', href=True)

        cog_div = bs.find('div', class_='mw-body-content mw-content-ltr')

        # getting the names
        if cog_div:
            # obtain link
            links = cog_div.find_all('a', href=True)
            counter = 0

            for link in links:
                if 'title' in link.attrs:
                    if 'href' in link.attrs:
                        # these cogs dont have images

                        # create the tuple and append it
                        tuple = (counter, link['title'], str(link['title']).lower(), 'https://corporateclash.wiki.gg' + str(link['href']), '')
                        cogs.append(tuple)
                        counter += 1

    # iterate through operations analysts cog names
    if r3.status_code == 200:
        # parsing the content
        bs = BeautifulSoup(r3.content, 'html.parser')

        cog_div = bs.find('div', class_='mw-body-content mw-content-ltr')

        # getting the names
        if cog_div:
            # obtain link
            links = cog_div.find_all('a', href=True)
            counter = 0

            for link in links:
                if 'title' in link.attrs:
                    if 'href' in link.attrs:
                        # images would be found here but those cogs dont have images :(

                        # create the tuple and append it
                        tuple = (counter, link['title'], str(link['title']).lower(), 'https://corporateclash.wiki.gg' + str(link['href']), '')
                        cogs.append(tuple)
                        counter += 1


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


# gets
def get_cog_with_id(id):
    for cog in cogs:
        if cog[4] == id:
            return cog


def get_cog_with_name(name):
    if not does_cog_exist(name):
        return

    for cog in cogs:
        if cog[2] == name:
            return cog


def get_cog_name(cog):
    print(cog)
    print(cog[1])
    return cog[1]


def get_names():
    names = []
    for c in cogs:
        names.append(c[1])
    return names


# name for use with commands
def get_id_names():
    id_names = []
    for c in cogs:
        id_names.append(c[2])
    return id_names


def does_cog_exist(name):
    if name in get_id_names():
        return True


def get_cog_url(name):
    return get_cog_with_name(name)[3]


def get_cog_image(name):
    return get_cog_with_name(name)[4]

