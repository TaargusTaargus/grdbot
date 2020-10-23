from asyncio import sleep
from discord import Embed
from goodreads import review
from good_reads_utilities import resolve_book, resolve_user, resolve_user_activity, resolve_update_embed
from random import choice


import test

ACTIVITY_COMMAND_ERROR = f'Was unable to retrieve most recent user activity.'
BOOK_COMMAND_ERROR = f'Was unable to find a matching book.'
FOLLOW_COMMAND_ERROR = f'Was unable to follow specified user.'
QUOTE_COMMAND_ERROR = f'All out of quotes.'
RATING_COMMAND_ERROR = f'Unable to fetch rating for this book.'
REVIEW_COMMAND_ERROR = f'Unable to find a review.'

DISPLAY_NUM_ACTIVITIES = 5

QUOTES = [
    'A barrel in the bush is worth a bird in the bucket.',
    'Two birds, two stones.',
    'Time can be measured by dollars.',
    'I know nuclear, believe me!'
]

class CommandQueue:

    API_INTERVAL = 2
    
    def __init__( self, good_reads_client ):
        self.good_reads_client = good_reads_client
        self.run_queue = []
        self.waiting = False

    
    async def add_command( self, channel, command, input_text ):
        if self.waiting:
            self.run_queue.append( ( channel, command, input_text ) )
        else:
            await self.run_command( channel, command, input_text )
            

    async def run_command( self, channel, command, input_text ):
        self.waiting = True
        
        print( command[ 'name' ] + " " + input_text )
        await command[ 'fx' ]( channel, self.good_reads_client, input_text )
        await sleep( self.API_INTERVAL )

        if len( self.run_queue ):
            await self.run_command( *self.run_queue.pop( 0 ) )
        else:
            self.waiting = False


async def activity_command( channel, good_reads_client, user_key ):
    updates = resolve_user_activity( good_reads_client, user_key )
    total_n = min( len( updates ), DISPLAY_NUM_ACTIVITIES )
    await channel.send( f'Here are the latest updates from {user_key} on GoodReads:' if len( updates ) else f'This user has no activity yet.' )
    for n in range( 1, total_n + 1 ):
        update = updates[ n - 1 ]
        await channel.send( embed=resolve_update_embed( user_key, update ) )


async def book_command( channel, good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        await channel.send( f'{book.title} by {book.authors[ 0 ].name} has an average rating on GoodReads of {book.average_rating} / 5 stars.' )
    else:
        await channel.send( BOOK_COMMAND_ERROR )


async def quote_command( channel, good_reads_client, user_key ):
    await channel.send( choice( QUOTES ) )
 

async def rating_command( channel, good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        await channel.send(  f'{book.title} by {book.authors[ 0 ].name} has an average rating on GoodReads of {book.average_rating} / 5 stars.' )
    else:
        await channel.send( RATING_COMMAND_ERROR )


async def review_command( channel, good_reads_client, text ):
    text = text.split()
    book_key = " ".join( text[ 1: ] )
    user_key = text[ 0 ]
    book = resolve_book( good_reads_client, book_key )
    user = resolve_user( good_reads_client, user_key )
    try:
        resp = user._client.request(
            "/review/show_by_user_and_book.xml",
            { 'user_id': user.gid, 'book_id': book.gid }
        )
        embed = Embed()
        rev = review.GoodreadsReview( resp[ 'review' ] )
        embed.set_image( url = rev._review_dict[ 'book' ][ 'image_url' ] )
        embed.description =  f'{rev.rating}/5' + ( f': {rev.body}' + ( '' if rev.body.strip()[ -1 ] in '.!?' else '...' ) if rev.body else '' )
        embed.title = f"{user.user_name}'s review for {book.title} by {book.authors[ 0 ].name}"
        embed.url = rev._review_dict[ 'url' ]
        await channel.send( embed = embed )
    except:
        await channel.send( REVIEW_COMMAND_ERROR )

