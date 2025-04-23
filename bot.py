import datetime
from pytoontown.corporateclash import *
import requests
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import employees
import managers

# setting up command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# set up api connections
cc = CorporateClashAPI()

# variables for tracking
tracking = ''
recently_tracked = []  # list of the districts that were just scanned for tracking


# refresh api content
def refresh():
    cc.refresh()


# returns a message containing every invasion in districts right now
def current_invasions():
    refresh()
    districts = cc.districts()

    # iterate through districts and determine which ones have an invasion


# used for tracking an invasion for a specific cog.
def track_districts():
    return 0


# returns a district containing the inputted cog if it exists
def check_for_cog_invasion(cog):
    for district in recently_tracked:
        if cog == district['cogs_attacking']:
            return district


# compare invasions from prior to refresh and after refresh to determine if any new invasions were added
def compare_invasions():
    pass


# startup
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    # obtain cog information
    employees.get_valid_cogs()
    managers.get_valid_managers()


# message parser & bootstrap
@bot.event
async def on_message(message):
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('!invasions'):
        await on_invasion(message)
    if message.content.startswith('!population') or message.content.startswith('!pop'):
        await on_population(message)
    if message.content.startswith('!tracker'):
        await on_tracker(message)
    if message.content.startswith('!districtinformation') or message.content.startswith('!dinfo'):
        await on_district_information(message)
    if message.content.startswith('!help') or message.content.startswith('!info'):
        await on_help(message)
    if message.content.startswith('!wiki'):
        await on_wiki(message)
    if message.content.startswith('!cogspawns') or message.content.startswith('!cs'):
        await on_cog_spawns(message)
    if message.content.startswith('!exe'):
        await on_exe(message)


# displays any invasions currently active
@bot.event
async def on_invasion(message):
    refresh()

    # gather information about districts
    districts = cc.districts()
    invaded_districts = []

    # error
    if districts is None:
        await message.channel.send('Currently unable to fetch district information.')
        return

    # iterate through districts and store currently occupied ones
    for district in districts:
        if district.get('invasion_online', True):
            invaded_districts.append(district)

    if invaded_districts:
        embed = discord.Embed(
            title="Currently Invaded Districts",
            colour=0x4a5691
        )
        embed.set_thumbnail(url='https://corporateclash.wiki.gg/images/thumb/3/3a/MpCogs.png/450px-MpCogs.png')

        # for each district, add a field
        for district in invaded_districts:
            cog_attacking = district.get('cogs_attacking')
            fv = ('Cog: ' + f'**' + cog_attacking + f'**' + '\nRemaining Time: ' + str(
                datetime.timedelta(seconds=district.get('remaining_time')))
                  + '\nCog Threshold: ' + str(district.get('count_total'))
                  + '\nCogs Defeated: ' + str(district.get('count_defeated')))
            embed.add_field(name=f'__'+district.get('name')+f'__', value=fv)

        await message.channel.send(embed=embed)
    elif len(invaded_districts) == 0:
        await message.channel.send('No districts are currently under invasion!')


# displays the current population of toontown: corporate clash
@bot.event
async def on_population(message):
    r = requests.get('https://corporateclash.net/api/v1/game_info.js')

    # parse request
    if r.status_code == 200:
        data = r.json()
        num_toons = data.get('num_toons')
        if num_toons is not None:
            # creating the embed
            embed = discord.Embed(
                title="Population",
                colour=0x4a5691
            )
            embed.add_field(name='', value=num_toons)
            embed.set_thumbnail(url='https://corporateclash.wiki.gg/images/thumb/b/b2/MpToons.png/450px-MpToons.png')

            # send the message with the population
            await message.channel.send(embed=embed)

        if num_toons is None:
            m = 'Population is unavailable right now.'
            await message.channel.send(m)


# used for tracking a specific cog
@bot.event
async def on_tracker(message):
    # parse cog name
    cog = parse_cog(message)

    # ensure that input is not empty
    if cog is None:
        await message.channel.send('Please input the name of the cog you\'d like to track.')
        return

    # verify the cog exists, first by checking if it exists in the list of standard cogs
    if cog in employees.get_id_names():
        embed = discord.Embed(
            colour=0x4a5691
        )
        embed.add_field(name='Now tracking invasions for: ', value=employees.get_cog_with_name(cog)[1])
        embed.add_field(name='', value='')
        url = employees.get_cog_url(cog)
        embed.add_field(name='', value="[wiki.gg](" + url + ")")

        # set thumbnail to be image of cog
        embed.set_thumbnail(url=employees.get_cog_image(cog))

        # temp
        embed.set_footer(text='Note: tracking function is currently not implemented.')

        await message.channel.send(embed=embed)
    # check if the cog exists in the list of managers
    elif cog in managers.get_id_names():
        await message.channel.send('Managers cannot be tracked for invasions.')
    else:
        await message.channel.send('That appears to be an invalid cog name or the cog is currently not supported for tracking.')


# displays information on all districts online
@bot.event
async def on_district_information(message):
    refresh()

    districts = cc.districts()
    online_districts = []

    # error
    if districts is None:
        await message.channel.send('Currently unable to fetch district information.')
        return

    # iterate through districts and store currently occupied ones
    for district in districts:
        if district.get('district_online', True):
            online_districts.append(district)

    if online_districts:
        embed = discord.Embed(
            title="Currently Online Districts",
            colour=0x4a5691
        )
        embed.set_thumbnail(
            url='https://static.wikia.nocookie.net/toontown/images/2/24/Districts.png/revision/latest?cb=20211203021758')

        # for each district, add a field
        for district in online_districts:
            fv = 'Population: ' + str(district.get('population'))

            if district.get('invasion_online', True):
                fv += '\n'f'***!Under Invasion!***' + ('\nCog: ' + district.get('cogs_attacking')
                + ('\nRemaining Time: ' + str(datetime.timedelta(seconds=district.get('remaining_time')))))
            embed.add_field(name=f'__'+district.get('name')+f'__', value=fv)

        await message.channel.send(embed=embed)


# displays all commands
@bot.event
async def on_help(message):
    embed = discord.Embed(
        title="Help",
        colour=0x4a5691
    )
    italicized_invasions = f"*!invasions*"
    embed.add_field(name='Commands', value=f'**Current Invasions**' ' - Retrieves current districts with active invasions, displaying the invading cog, the remaining amount of time, the threshold of cogs that must be defeated for the invasion to end, and the amount of cogs defeated. - ' + f'*!invasions*'
                    + '\n\n'f'**Population**' ' - Retrieves the current population of ToonTown: Corporate Clash. - ' + f'*!population* or *!pop*'
                    + '\n\n'f'**Tracker**' ' - Allows the user to enter a cog for the bot to track. The bot will send the user a message notifying that an invasion with '
                    + 'the tracked cog is available. - ' + f'*!tracker cog_name*'
                    + '\n\n'f'**District Information**' ' - Retrieves the information of every district currently online. - ' f'*!districtinformation* or *!dinfo*'
                    + '\n\n'f'**Help**' ' - Bot usage and information. - ' f'*!help* or *!info*')
    embed.add_field(name='Settings', value=f'**Notify for new Invasions**' ' - Toggle receiving a message for every new invasion. - ' f'*!notifyinvasions*'
                    + '\n\n'f'**Clear Tracked Cog**' ' - Remove the currently tracked cog. - ' f'*!clear*'
                    + '\n\nFor more information, type ' f'*!help2*')
    embed.set_thumbnail(url='https://corporateclash.wiki.gg/images/thumb/a/a4/DiceSticker2023.png/180px-DiceSticker2023.png')

    # send the message with the population
    await message.channel.send(embed=embed)


# returns a chart from the wiki displaying street spawn percentages
@bot.event
async def on_cog_spawns(message):
    embed = discord.Embed(
        title="Street Cog Spawn Chart",
        color=0x4a5691
    )
    embed.set_image(url='https://corporateclash.wiki.gg/images/thumb/0/0f/StreetCogSpawnChart.png/700px-StreetCogSpawnChart.png')
    await message.channel.send(embed=embed)


# returns a chart from the wiki displaying exe street spawn percentages
@bot.event
async def on_exe(message):
    embed = discord.Embed(
        title="EXE Street Cog Spawn Chart",
        color=0x4a5691
    )
    embed.set_image(url='https://corporateclash.wiki.gg/images/thumb/a/a6/Execha.png/626px-Execha.png')
    await message.channel.send(embed=embed)


# used for returning basic information about a cog and a wiki link
@bot.event
async def on_wiki(message):
    # parse the cog name
    cog = parse_cog(message)

    # verify if cog name is returned
    if cog is None:
        await message.channel.send('Please input the name of the cog you\'d like to get information about.')
        return

    # verify the cog exists in the regular list of employees
    if cog in employees.get_id_names():
        embed = discord.Embed(
            title=employees.get_cog_with_name(cog)[1]+" Information",
            colour=0x4a5691
        )

        # add the url to the cog
        url = employees.get_cog_url(cog)

        # getting the cog image
        r = requests.get(url)

        image_url = ''
        # iterate through cog names
        if r.status_code == 200:
            # parsing the content
            bs = BeautifulSoup(r.content, 'html.parser')
            cog_div = bs.find('div', class_='mw-body-content mw-content-ltr')

            # wiki info
            info_div = bs.find('aside', class_='portable-infobox')

            if info_div:
                # adding image
                figure = info_div.find('figure', class_='pi-image')
                if figure:
                    img_tag = figure.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = 'https://corporateclash.wiki.gg' + img_tag.get('src')

                # adding cog department
                dept = info_div.find('div', {'data-source': 'department'}).find('div').text.strip()
                pos = info_div.find('div', {'data-source': 'position'}).find('div').text.strip()

                # adding the level values
                low_level_element = info_div.find('td', {'data-source': 'lowest_level'})
                high_level_element = info_div.find('td', {'data-source': 'highest_level'})

                # strip the text
                low_level = low_level_element.text.strip()
                high_level = high_level_element.text.strip()

                # adding cog damage range
                low_dam = info_div.find('td', {'data-source': 'lowest_damage'}).text.strip()
                high_dam = info_div.find('td', {'data-source': 'highest_damage'}).text.strip()

                # create the embeds
                create_wiki_embed_for_employee(embed, dept, pos, low_level, high_level, low_dam, high_dam, url, image_url)

        await message.channel.send(embed=embed)
    # verify if the cog exists in the manager list of employees
    elif cog in managers.get_id_names():
        embed = discord.Embed(
            title=managers.get_cog_with_name(cog)[1]+" Information",
            colour=0x4a5691
        )

        # add the url to the cog
        url = managers.get_cog_url(cog)

        # getting the cog image
        r = requests.get(url)

        image_url = ''
        # iterate through cog names
        if r.status_code == 200:
            # parsing the content
            bs = BeautifulSoup(r.content, 'html.parser')

            # wiki info
            info_div = bs.find('aside', class_='portable-infobox')

            if info_div:
                # adding image
                figure = info_div.find('figure', class_='pi-image')
                if figure:
                    img_tag = figure.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = 'https://corporateclash.wiki.gg' + img_tag.get('src')

            if info_div:
                # adding cog department
                dept = info_div.find('div', {'data-source': 'department'}).find('div').text.strip()
                pos = info_div.find('div', {'data-source': 'position'}).find('div').text.strip()

                # adding the stats
                hp = info_div.find('div', {'data-source': 'hp'}).find('div').text.strip()
                defense = info_div.find('div', {'data-source': 'defense'}).find('div').text.strip()
                level = info_div.find('td', {'data-source': 'level'}).text.strip()

                # adding cog damage range
                low_dam = info_div.find('td', {'data-source': 'lowest_damage'}).text.strip()
                high_dam = info_div.find('td', {'data-source': 'highest_damage'}).text.strip()

                # create the embeds
                create_wiki_embed_for_mgr(embed, dept, pos, hp, defense, level, low_dam, high_dam, url, image_url)

        await message.channel.send(embed=embed)
    else:
        await message.channel.send('That appears to be an invalid cog name or the cog currently does not have a wiki article.')


# paring cog name from message
def parse_cog(message):
    # split the message
    parse = str(message.content).split(' ')

    # verify usage
    if len(parse) < 2:
        return

    # parse the cog name
    cog_name = ''
    for p in parse:
        if p != parse[0]:
            cog_name += p + ' '

    # parse cog from inputted message
    cog = cog_name.lower().strip()

    return cog


# creating embeds for wiki
def create_wiki_embed_for_employee(embed, dept, pos, low_lev, high_lev, low_damage, high_damage, url, image_url):
    # add the dept and pos and spacer
    embed.add_field(name='Department: ', value=dept)
    embed.add_field(name='Position: ', value=pos + '\n')
    embed.add_field(name='', value='')

    # adding the level ranges
    embed.add_field(name='Levels: ', value='\nLowest Level: ' + str(low_lev) + '\nHighest Level: ' + str(high_lev))

    # adding the damage ranges
    embed.add_field(name='Damage Range: ',
                    value='\nLowest Damage: ' + str(low_damage) + '\nHighest Damage: ' + str(high_damage))

    # embedding the image and sending the message
    embed.set_thumbnail(url=image_url)
    embed.add_field(name='', value="[wiki.gg](" + url + ")", inline=False)


def create_wiki_embed_for_mgr(embed, dept, pos, hp, defense, level, low_damage, high_damage, url, image_url):
    # add the dept and pos and spacer
    if dept is not None:
        embed.add_field(name='Department: ', value=dept)
    if pos is not None:
        embed.add_field(name='Position: ', value=pos + '\n')
    embed.add_field(name='', value='')

    # adding the stats
    if hp is not None:
        embed.add_field(name='HP: ', value=str(hp))
    if defense is not None:
        embed.add_field(name='Defense: ', value=str(defense))
    if level is not None:
        embed.add_field(name='Level: ', value=str(level))

    # adding the damage ranges
    if high_damage is not None and low_damage is not None:
        embed.add_field(name='Damage Range: ',
                    value='\nLowest Damage: ' + str(low_damage) + '\nHighest Damage: ' + str(high_damage))

    # embedding the image and sending the message
    embed.set_thumbnail(url=image_url)
    embed.add_field(name='', value="[wiki.gg](" + url + ")", inline=False)


bot.run('discord-api-key-here')
