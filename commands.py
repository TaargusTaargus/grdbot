from asyncio import sleep
from goodreads import review
from good_reads_follower import FollowManager
from good_reads_utilities import resolve_book, resolve_user, resolve_user_activity, resolve_update_message
from random import choice


import test

ACTIVITY_COMMAND_ERROR = f'Was unable to retrieve most recent user activity.'
BOOK_COMMAND_ERROR = f'Was unable to find a matching book.'
FOLLOW_COMMAND_ERROR = f'Was unable to follow specified user.'
QUOTE_COMMAND_ERROR = f'All out of quotes.'
RATING_COMMAND_ERROR = f'Unable to fetch rating for this book.'
REVIEW_COMMAND_ERROR = f'Unable to find a review.'

DISPLAY_NUM_ACTIVITIES = 5

HELP_TEXT_HEADER = f'''
This is the GoodReads D-bot speaking, thanks for forcing me to be your slave.
I currently respond to the following commands:

'''

QUOTES = [
    'A barrel in the bush is worth a bird in the bucket.',
    'Two birds, two stones.',
    'Time can be measured by dollars.',
    'I know nuclear, believe me!'
]

class CommandQueue:

    API_INTERVAL = 2
    
    def __init__( self, good_reads_client  ):
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
        
        #try:
        ret = command[ 'fx' ]( channel, self.good_reads_client, input_text )
        #except Exception as e:
            #print( e )
            #ret = command[ 'error' ]
        if ret:
            await channel.send( ret )

        await sleep( self.API_INTERVAL )

        if len( self.run_queue ):
            await self.run_command( *self.run_queue.pop( 0 ) )
        else:
            self.waiting = False


follow_manager = FollowManager()

async def start_follow_manager( command_q ):
    await follow_manager.start_scan( command_q )


def activity_command( channel, good_reads_client, user_key ):
    updates = resolve_user_activity( good_reads_client, user_key )
    total_n = min( len( updates ), DISPLAY_NUM_ACTIVITIES )
    text = f'Here are the latest updates from {user_key} on GoodReads:' if len( updates ) else f'This user has no activity yet.'
    for n in range( 1, total_n + 1 ):
        update = updates[ n - 1 ]    
        text = text + f'\n{n}. ' + resolve_update_message( user_key, update )
            
    return text


def book_command( channel, good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        return f'{book.title} by {book.authors[ 0 ].name} has an average rating on GoodReads of {book.average_rating} / 5 stars.'
    else:
        return BOOK_COMMAND_ERROR


def quote_command( channel, good_reads_client, user_key ):
    return choice( QUOTES )
 

def rating_command( channel, good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        return f'{book.title} by {book.authors[ 0 ].name} has an average rating on GoodReads of {book.average_rating} / 5 stars.'
    else:
        return RATING_COMMAND_ERROR


def review_command( channel, good_reads_client, text ):
    text = text.split()
    book_key = " ".join( text[ 1: ] )
    user_key = text[ 0 ]
    book = resolve_book( good_reads_client, book_key )
    user = resolve_user( good_reads_client, user_key )
    try:
        resp = user._client.request(
            "/review/show_by_user_and_book.xml",
            {'user_id': user.gid, 'book_id': book.gid }
        )
        rev = review.GoodreadsReview( resp[ 'review' ] )
        body = rev.body[ : rev.body.rfind( '.' ) + 1 ] if rev.body else None
        return ( f'{user.user_name} gave {book.title} by {book.authors[ 0 ].name} {rev.rating} / 5 stars on GoodReads.\n{user.user_name} wrote (might be cut-off): "{body}"'
                        if body else
               f'{user.user_name} gave {book.title} by {book.authors[ 0 ].name} {rev.rating} / 5 stars on Goodreads.' )
    except:
        return REVIEW_COMMAND_ERROR


def help_command( channel, good_reads_client, text ):
    text = ''
    for key in COMMANDS:
        if len( COMMANDS[ key ][ 'args' ] ):
            text = text + '\n'.join( [ f'{key} {arg}' for arg in COMMANDS[ key ][ 'args' ] ] )
        else:
            text = text + f'{key}'
        text = text + '\n' + COMMANDS[ key ][ 'description' ] + '\n\n'
    return HELP_TEXT_HEADER + text


COMMANDS = {
    '\\activity': {
        'args': [ '[username]' ],
        'description': 'Will return the most recent GoodReads activity for the given user.',
        'error': ACTIVITY_COMMAND_ERROR,
        'fx': activity_command,
        'test': test.run_activity_command_test
    },
    '\\book': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return book title, author, and description based on id or book name from the GoodReads website.',
        'error': BOOK_COMMAND_ERROR,
        'fx': book_command
    },
    '\\follow': {
        'args': [ '[username]', '[user-id]' ],
        'description': 'Will follow the specified user and provide updates as they appear on the GoodReads website.',
        'error': FOLLOW_COMMAND_ERROR,
        'fx': follow_manager.follow_command
    },
    '\\help': {
        'args': [],
        'description': 'Will return help text with usage information.',
        'error': 'Unknown error.',
        'fx': help_command
    },
    '\\quote': {
        'args': [],
        'description': 'Will return an inspiring quote.',
        'error': QUOTE_COMMAND_ERROR,
        'fx': quote_command
    },
    '\\rating': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return the GoodReads rating for the book with author and title.',
        'error': RATING_COMMAND_ERROR,
        'fx': rating_command
    },
    '\\review': {
        'args': [ '[username] [book-id]', '[username] [book-name]' ],
        'description': 'Will return the specified GoodReads review from user.',
        'error': REVIEW_COMMAND_ERROR,
        'fx': review_command
    }
}
