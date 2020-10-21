# good-reads-discord-bot.py
import commands
import discord
import os
import test

from dotenv import load_dotenv
from goodreads import client
from good_reads_follower import FollowManager
from sys import argv

load_dotenv()

DISCORD_TOKEN = os.getenv( 'DISCORD_TOKEN' )
GOOD_READS_KEY = os.getenv( 'GOOD_READS_KEY' )
GOOD_READS_SECRET = os.getenv( 'GOOD_READS_SECRET' )
FOLLOWERS_LIST_HANDLE = 'followers.json'
HELP_TEXT_TITLE = f'''grdbot: The handsomest D-Bot for accessing GoodReads'''
HELP_TEXT_HEADER = f'''
This is the GoodReads D-bot speaking, thanks for forcing me to be your slave.
I currently respond to the following commands:

'''

good_reads_client = client.GoodreadsClient( GOOD_READS_KEY, GOOD_READS_SECRET )

command_q = commands.CommandQueue( good_reads_client )
discord_client = discord.Client()
follow_manager = FollowManager()

COMMANDS = {
    '\\activity': {
        'args': [ '[username]' ],
        'description': 'Will return the most recent GoodReads activity for the given user.',
        'error': commands.ACTIVITY_COMMAND_ERROR,
        'fx': commands.activity_command,
        'test': test.run_activity_command_test
    },
    '\\book': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return book title, author, and description based on id or book name from the GoodReads website.',
        'error': commands.BOOK_COMMAND_ERROR,
        'fx': commands.book_command
    },
    '\\follow': {
        'args': [ '[username]', '[user-id]' ],
        'description': 'Will follow the specified user and provide updates as they appear on the GoodReads website.',
        'error': commands.FOLLOW_COMMAND_ERROR,
        'fx': follow_manager.follow_command
    },
    '\\quote': {
        'args': [],
        'description': 'Will return an inspiring quote.',
        'error': commands.QUOTE_COMMAND_ERROR,
        'fx': commands.quote_command
    },
    '\\rating': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return the GoodReads rating for the book with author and title.',
        'error': commands.RATING_COMMAND_ERROR,
        'fx': commands.rating_command
    },
    '\\review': {
        'args': [ '[username] [book-id]', '[username] [book-name]' ],
        'description': 'Will return the specified GoodReads review from user.',
        'error': commands.REVIEW_COMMAND_ERROR,
        'fx': commands.review_command
    }
}


@discord_client.event
async def on_ready():
    print( f'{discord_client.user} has connected to Discord!' )
    channels = {}
    for guild in discord_client.guilds:
        print(
            f'{discord_client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
        for chan in guild.channels:
            channels[ chan.id ] = chan
        
    if not follow_manager.scanning:
        await follow_manager.start_scan( command_q, channels, FOLLOWERS_LIST_HANDLE )


@discord_client.event
async def on_member_join( member ):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, this is the GoodReads D-Bot reaching out to you! Type "\\help" in chat to get a list of my features.'
    )


@discord_client.event
async def on_message( message ):
    if message.author.bot:
        return

    words = message.content.split()

    if words[ 0 ] in COMMANDS:
        await command_q.add_command(
            message.channel,
            COMMANDS[ words[ 0 ] ],
            " ".join( words[ 1: ] )
        )
    elif words[ 0 ] in '\\help':
        embed = discord.Embed()
        text = ''
        for key in COMMANDS:
            if len( COMMANDS[ key ][ 'args' ] ):
                text = text + '\n'.join( [ f'**{key} {arg}**' for arg in COMMANDS[ key ][ 'args' ] ] )
            else:
                text = text + f'{key}'
            text = text + '\n' + COMMANDS[ key ][ 'description' ] + '\n\n'
        embed.description = HELP_TEXT_HEADER + text
        embed.title = HELP_TEXT_TITLE
        await message.channel.send( embed = embed )
    elif words[ 0 ][ 0 ] == '\\':
        await message.channel.send( "You talkin' about me? You talkin' about me?! Type '\help' if you were actually talkin' about me." )       
    

discord_client.run( DISCORD_TOKEN )
