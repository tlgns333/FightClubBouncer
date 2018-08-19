#! python3
# coding: utf-8

import json
import logging
import random
import sys
import datetime

import discord
from discord.ext import commands

from ext.utils import checks

# logging
logging.basicConfig(level=logging.WARNING)


# JSON load
def load_db():
    with open('db.json') as f:
        return json.load(f)


# Database load
db = load_db()

# bot declaration
prefix = db['prefix']

description = '''Hello! I'm Apollo, margobra8's multipurpose Discord bot.
I run with Python 3.5.\n
One of my main utilities is an AdBlock for users links in nicknames.
But there are a lot of other commands I can run and things I can do.'''
bot = commands.Bot(command_prefix=prefix, description=description, no_pm=True, pm_help=True)

# ads declaration/banning from db
ads = db['ads']
# ads = [".biz"] # tests only
whitelist = db['whitelist']
role_whitelist = db['role_whitelist']
current_datetime = datetime.datetime.now().strftime("%d %b %Y %H:%M")

# Cogs addition
initial_extensions = [
    'ext.admin',
    'ext.mentions',
    'ext.meta',
    'ext.mod',
    # 'ext.profile',
]


# Error handling
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author,
                               '[ERROR:NoPrivateMessage] Sorry. This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.channel,
                               '[ERROR:DisabledCommand] Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        pass  # do nothing

    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(ctx.message.channel,
                               "[ERROR:CheckFailure] Sorry. You don't have enough permissions to run this command.")
    elif isinstance(error, commands.CommandNotFound):
        await bot.send_message(ctx.message.channel,
                               "[ERROR:CmdNotFound] Sorry. The command you requested doesn't exist.")


@bot.event
async def on_ready():
    print('\nLogged in as')
    print("User: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("Instance run at: " + current_datetime)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    await bot.change_status(game=discord.Game(name="%help | v.1.5"), idle=False)


@bot.event
async def on_resumed():
    print('resumed...')


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        print("{0} has updated its nickname".format(after))
        for word in ads:
            if word.lower() in str(after.nick).lower():
                try:
                    alert = '{0.mention} nickname violates the guidelines, removing...'
                    await bot.send_message(after.server, alert.format(after))
                    await bot.change_nickname(after, '[Nick violates rules]')
                except discord.HTTPException:
                    error = "There was an error changing {0.mention} nickname."
                    await bot.send_message(after.server, error.format(after))
            else:
                continue


@bot.event
async def on_server_join(server):
    await bot.send_message(server, "Hello @everyone! I've just joined here!, please enable nickname permissions \
                                   so that I can run my commands and functions properly!")


@bot.command(hidden=True)
@checks.is_owner()
async def user_list():
    """Displays a log of all users in every server the bot is connected to"""
    print("!!!!usrlist!!!! Scanning Servers and nicknames as requested")
    await bot.say("A list of the users in the servers has been logged into the bot console.")
    print("\nLog datetime: " + current_datetime)
    print("----------------------")
    for server in bot.servers:
        for member in server.members:
            print(
                "server: {0} | user: {1.name} | user_id: {1.id} | role: {1.top_role} | role_id: {1.top_role.id}".format(
                    server, member,
                    member))


@bot.command(hidden=True)
async def date_joined(member: discord.Member):
    """Says when a member joined from the bot server's database"""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))


# run dat shit tho
if __name__ == '__main__':
    if any('debug' in arg.lower() for arg in sys.argv):
        bot.command_prefix = '^'

    bot.client_id = db['client_id']
    bot.carbon_key = db['carbon_key']  # Future carbon integration???? well never know
    bot.bots_key = db['bots_key']

    # load the extensions
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(db['XggawxayBQbSE3yB4AXQw60T8Pi16Iq9'])
