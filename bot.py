import json
import os
import platform
import random
import sys
from discord.ext.commands.core import command
import requests
from lxml import html
from ast import literal_eval

# uWu quote libraries
from owoify import owoify

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

if not os.path.isfile("sources.json"):
    sys.exit("'sources.json' not found! Please add it and try again.")
else:
    with open("sources.json") as file:
        sources = json.load(file)

if not os.path.isfile("mangas.json"):
    sys.exit("'mangas.json' not found! Please add it and try again.")
else:
    with open("mangas.json") as file:
        mangas = json.load(file)

if not os.path.isfile("users.json"):
    sys.exit("'users.json' not found! Please add it and try again.")
else:
    with open("users.json") as file:
        users = json.load(file)

if not os.path.isfile("quotes.json"):
    sys.exit("'quotes.json' not found! Please add it and try again.")
else:
    with open("quotes.json") as file:
        quotes = json.load(file)

intents = discord.Intents.default()

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()

# Setup the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = ["Degeneracy!"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))

def write_mangas(new_data, old_data, filename):
    with open(filename,'r+') as file:
        old_data['mangas'].append(literal_eval(new_data))
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(old_data, file, indent = 4)

def write_sources(new_data, old_data, filename):
    with open(filename,'r+') as file:
        old_data['sources'].append(literal_eval(new_data))
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(old_data, file, indent = 4)

def write_users(new_data, old_data, filename):
    with open(filename,'r+') as file:
        old_data['users'].append(literal_eval(new_data))
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(old_data, file, indent = 4)

def page_request(url):
    request = requests.get(url).text
    tree = html.fromstring(request)
    return tree

def xpath_scrape(tree, pattern, href):
    if href == True:
        return tree.xpath("/"+pattern+"/@href") or tree.xpath("/"+pattern+"[text()]/@href")
    else:
        return tree.xpath("/"+pattern+"/text()")

# Get manga data
def scan_source(args):
    for i in sources['sources']:
        if i['link'] in args:
            tree = page_request(args)
            name = xpath_scrape(tree, i['name_xpath'], False)[0]
            link = args
            last_updated = xpath_scrape(tree, i['last_updated_xpath'], False)[0]
            current_chapter = xpath_scrape(tree, i['chapter_xpath'], False)[0]
            chapter_link = i['link']+xpath_scrape(tree, i['chapter_link'], True)[0]

            return str(name), str(link), str(last_updated), str(current_chapter), str(chapter_link)
    
    return "", "", "", "", ""

def add_manga(mangas, name, link, last_updated, current_chapter, chapter_link):

    manga = {
        "name": name,
        "link": link,
        "last_updated": last_updated,
        "current_chapter": current_chapter,
        "chapter_link": chapter_link
        }

    manga = json.dumps(manga)

    write_mangas(manga, mangas, 'mangas.json')

    with open("mangas.json") as file:
        mangas = json.load(file)

    return

def del_manga(users, user, list_mangas, name):

    flags=0
    for j in users['users']:
        if user == j['name']:
            for k in j['mangas']:
                if name == k:
                    flags += 1

    if flags == 1:
        for j in users['users']:
            if user == j['name']:
                count = 0
                for l in j['mangas']:
                    count += 1
                    if l == name:
                        break

                j['mangas'].pop(count-1)

                users = json.dumps(users)

                with open('users.json','w') as file:
                    json.dump(literal_eval(users), file, indent = 4)

                with open("users.json") as file:
                    users = json.load(file)

                return True

    else:
        return False

def add_source(sources, args):

    source = {
        "name": args[2],
        "link": args[3],
        "name_xpath": args[4],
        "last_updated_xpath": args[5],
        "chapter_xpath": args[6]
    }

    source = json.dumps(source)

    write_sources(source, sources, 'sources.json')

    with open("sources.json") as file:
        sources = json.load(file)

    return

def user_add(users, user, name):

    flags=0
    for j in users['users']:
        if user == j['name']:
            for k in j['mangas']:
                if name == k:
                    flags += 1

    if flags == 0:
        for j in users['users']:
            if user == j['name']:
                j['mangas'].append(name)
    else:
        return "( ͡U ω ͡U ) Damn king, great choice...\nBut "+name+", already exists in your list!!!!"

    users = json.dumps(users)

    with open('users.json','w') as file:
        json.dump(literal_eval(users), file, indent = 4)

    with open("users.json") as file:
        users = json.load(file)

    return "\n"+name+", has been added to your list!!!!"

def create_user(users, user, id):

    print("creating user: "+user)

    user = {
        "id": id,
        "name": user,
        "mangas": []
    }

    user = json.dumps(user)

    write_users(user, users, 'users.json')

    with open("users.json") as file:
        users = json.load(file)

    return

def quote():

    length = len(quotes)
    key = random.randrange(length)

    msg = '"' + quotes[key]['Quote']+ '"\n - ' + quotes[key]['Author']

    return msg

def scan_mangas(mangas):

    updated_list = []
    for manga in mangas['mangas']:
        name, link, last_updated, current_chapter, chapter_link = scan_source(manga['link'])
        if last_updated != manga['last_updated']:
            
            updated_list.append(manga['name'])

            manga['last_updated'] = last_updated
            manga['current_chapter'] = current_chapter
            manga['chapter_link'] = chapter_link

    mangas = json.dumps(mangas)
    
    with open('mangas.json','w') as file:
        json.dump(literal_eval(mangas), file, indent = 4)

    with open("mangas.json") as file:
        mangas = json.load(file)

    return updated_list

def notify(user, updated_list):

    msg = ""

    for update in updated_list:
        if(len(list(filter (lambda x : x == update, user['mangas']))) > 0):
            for z in mangas['mangas']:
                if update == z['name']:
                    msg += z['chapter_link']+'\n'

    return msg

@tasks.loop(hours=6)
async def update():

    print("update() task started")
    updated_list = scan_mangas(mangas)

    # FlackShack#9395 232656557454655488
    # MugWuffun#9922 157616206843478016
    # MangaBot#1648 875534869566992434
    # AllWeNeedIsHope#4252 232680124854697987
    # jackosis214#1440 478800702097850369
    # Ztrider#3503 214940932972347392
    # SSMONEY#0049 426932687526166539
    # Slut for Instant Noodles (Devin)#6604 271107224691015681
    # Antacidsoup90#1310 300776017369235457
    # toocurly#1213 227176236034686976
    
    for user in users['users']:
        member = int(user['id'])
        member = await bot.fetch_user(member)
        
        tmp = notify(user, updated_list)
        if tmp:
            msg = "**New chapters inbound!**\n```"+tmp+"```"
            await member.send(msg)

    return

def help_msg():

    text = "**(◕‿◕) The following is a list of commands, senpai:** \n \
`@MangaSlave list` \n \
`@MangaSlave update` manually force an update of catalogue\n \
`@MangaSlave add [LINK/NAME]` \n \
`@MangaSlave del [NAME]` \n \
`@MangaSlave add [LINK],[LINK],[LINK]....` Mixed types works.\n \
`@MangaSlave del [NAME],[NAME],[NAME]....` \n \
`@MangaSlave source [NAME] [LINK] [xpath_to_name] [xpath_to_date_updated] [xpath_to_chapter/episode]` \n \
**Please do not use the source command unless you know what you are doing.**"

    return text

# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):

        user = str(message.author)

        message.content = ' '.join(message.content.split())

        lists_users = []
        for i in users['users']:
            lists_users.append(i['name'])
        
        list_mangas = []
        for i in mangas['mangas']:
            list_mangas.append(i['name'])


        if user not in lists_users:
            create_user(users, user, message.author.id)
            await message.author.send("Hurray! You were not important and did not exist before... You do now!")

        if "help" in message.content:
            await message.author.send(help_msg())
            return

        elif "update" in message.content:
            updated_list = scan_mangas(mangas)

            # FlackShack#9395 232656557454655488
            # MugWuffun#9922 157616206843478016
            # MangaBot#1648 875534869566992434
            # AllWeNeedIsHope#4252 232680124854697987
            # jackosis214#1440 478800702097850369
            # Ztrider#3503 214940932972347392
            # SSMONEY#0049 426932687526166539
            # Slut for Instant Noodles (Devin)#6604 271107224691015681
            # Antacidsoup90#1310 300776017369235457
            # toocurly#1213 227176236034686976
            
            for user in users['users']:
                member = int(user['id'])
                member = await bot.fetch_user(member)
                
                tmp = notify(user, updated_list)
                if tmp:
                    msg = "**New chapters inbound!**\n```"+tmp+"```"
                    await member.send(msg)

            return

        elif "add" in message.content:

            command = message.content.split(">")[1]
            arg = command.split(" ")[2::]

            arg = ' '.join(arg).split(",")

            for args in arg:
                if args.startswith("http"):

                    name, link, last_updated, current_chapter, chapter_link = scan_source(args)

                    if name == "":
                        msg = "(ㅅꈍ ˘ ꈍ) nishi-nishi, you made a fucksie-wucksie...\nSee the list command for current **sources**."
                        await message.author.send(msg)
                        continue

                    if name not in list_mangas:
                        add_manga(mangas, name, link, last_updated, current_chapter, chapter_link)
                        await message.author.send("(ᵘʷᵘ) "+name+", has been added to the archives!!!!")
                else:
                    if args in list_mangas:
                        name = args
                    else:
                        msg = "(ㅅꈍ ˘ ꈍ) nishi-nishi, you made a fucksie-wucksie...\nYou probs used the wrong names or added spaces before commas...\nSee the list command for current **mangas**."
                        await message.author.send(msg)
                        continue

                for i in mangas['mangas']:
                    if name.lower() == i['name'].lower():
                        flag = 0
                        for i in users['users']:
                            if user == i['name']:
                                flag += 1
                                msg = user_add(users, user, name)
                                await message.channel.send(msg)
                                continue

                        if flag == 0:
                            create_user(users, user, message.author.id)
                            msg = user_add(users, user, name)
                            await message.channel.send(msg)
                            continue
            return
        
        elif "del" in message.content:

            command = message.content.split(">")[1]
            arg = command.split(" ")[2::]

            arg = ' '.join(arg).split(",")

            for args in arg:
                if del_manga(users, user, list_mangas, args):
                    await message.author.send("(ᵘʷᵘ) "+args+", has been removed from your list!!!!")
                else:
                    await message.author.send("ಠ_ಠ Yeah there was some kinda error. Debugging is expensive.\nYou probs used the wrong names or added spaces before commas...")
            return

        elif "list" in message.content:
            msg = ""
            list = []
            msg += "These are the current sources:\n"
            for i in sources['sources']:
                list.append(i['link'])
            msg += "```" + str(list) + "```"

            await message.author.send(msg)

            list = []
            msg = "\nThis is the current library:\n"
            msg += "```"+ str(list_mangas) + "```"

            await message.author.send(msg)

            list = []
            msg = "\nThis is your watchlist:\n"
            await message.author.send(msg)
            for i in users['users']:
                if i['name'] == user:
                    list = i['mangas']

                    links = []
                    dates = []
                    for j in list:
                        for k in mangas['mangas']:
                            if str(j) == k['name']:
                                links.append(k['chapter_link'])
                                dates.append(k['last_updated'].split('-')[0])

                    for j in range(0,len(list)):
                        msg = "```["+list[j]+"]\n"+links[j]+"\n"+dates[j]+" ```\n"
                        await message.author.send(msg)

                    if list == "":
                        await message.author.send("```Nigga you need some sauce ༼ つ ◕_◕ ༽つ```")
                    break
            return

        elif "source" in message.content:
            args = message.content.split(">")[1]
            args = args.split(" ")

            name = args[2]

            for i in sources['sources']:
                if name.lower() == i['name'].lower():
                    await message.author.send("ಠ_ಠ This source, "+name+", already exists!!!!")
                    return

            add_source(sources, args)
            await message.author.send("(┐◎_◎┌) This source, "+name+", has been added to the list!!!!")     
            return

        elif "uwu" in message.content:
            msg = quote()
            msg = owoify(msg)
            await message.channel.send(msg)
            return
            

        else:
            await message.author.send(help_msg())
            return
        
        return


if __name__ == "__main__":

    update.start()

    # Run the bot with the token
    bot.run(config["token"])