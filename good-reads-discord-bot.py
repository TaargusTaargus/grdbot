# good-reads-discord-bot.py
import discord
import os
import test

from commands import AVAILABLE_COMMANDS
from dotenv import load_dotenv
from goodreads import client

load_dotenv()

DISCORD_TOKEN = os.getenv( 'DISCORD_TOKEN' )
GOOD_READS_KEY = os.getenv( 'GOOD_READS_KEY' )
GOOD_READS_SECRET = os.getenv( 'GOOD_READS_SECRET' )

discord_client = discord.Client()
good_reads_client = client.GoodreadsClient( GOOD_READS_KEY, GOOD_READS_SECRET )

@discord_client.event
async def on_ready():
    print( f'{discord_client.user} has connected to Discord!' )
    for guild in discord_client.guilds:
        print(
            f'{discord_client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )



@discord_client.event
async def on_member_join( member ):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, this is the GoodReads D-Bot reaching out to you!' + resolve_help_text()
    )


@discord_client.event
async def on_message( message ):
    if message.author.bot:
        return

    words = message.content.split()
    if words[ 0 ] in AVAILABLE_COMMANDS:
        try:
            ret = AVAILABLE_COMMANDS[ words[ 0 ] ][ 'fx' ](
                good_reads_client,
                " ".join( words[ 1: ] )
            )
        except Exception as e:
            print( e )
            ret = AVAILABLE_COMMANDS[ words[ 0 ] ][ 'error' ]
        await message.channel.send( ret )

    elif words[ 0 ][ 0 ] == '\\':
        await message.channel.send( "You talkin' about me? You talkin' about me?! Type '\help' if you were talkin' about me." )       

discord_client.run( DISCORD_TOKEN )
