from goodreads import review
from good_reads_utilities import resolve_book, resolve_user, resolve_user_activity
from random import choice

ACTIVITY_COMMAND_ERROR = f'Was unable to retrieve most recent user activity.'
BOOK_COMMAND_ERROR = f'Was unable to find a matching book.'
QUOTE_COMMAND_ERROR = f'All out of quotes.'
RATING_COMMAND_ERROR = f'Unable to fetch rating for this book.'
REVIEW_COMMAND_ERROR = f'Unable to find a review.'

DISPLAY_NUM_ACTIVITIES = 5

AVAILABLE_COMMANDS = {
    '\\activity': {
        'args': [ '[username]' ],
	'description': 'Will return the most recent activity for the given user.',
        'error': ACTIVITY_COMMAND_ERROR,
        'fx': lambda good_reads_client, text: activity_command( good_reads_client, text )
    },
    '\\book': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return book title, author, and description based on id or book name from the GoodReads website.',
        'error': BOOK_COMMAND_ERROR,
        'fx': lambda good_reads_client, text: book_command( good_reads_client, text )
    },
    '\\help': {
        'args': [],
        'description': 'Will return help text with usage information.',
        'error': None,
        'fx': lambda good_reads_client, text: HELP_TEXT_HEADER + help_command()
    },
    '\\quote': {
        'args': [],
        'description': 'Will return an inspiring quote.',
        'error': QUOTE_COMMAND_ERROR,
        'fx': lambda good_reads_client, text: quote_command()
    },
    '\\rating': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return the rating for the book with author and title.',
        'error': RATING_COMMAND_ERROR,
        'fx': lambda good_reads_client, text: rating_command( good_reads_client, text )
    },
    '\\review': {
        'args': [ '[username] [book-id]', '[username] [book-name]' ],
        'description': 'Will return most recent review from user.',
        'error': REVIEW_COMMAND_ERROR,
        'fx': lambda good_reads_client, text: review_command( good_reads_client, text )
    }
}

HELP_TEXT_HEADER = f'''
This is the GoodReads D-bot speaking, thanks for forcing me to be your slave.
I currently respond to the following commands:

'''

QUOTES = [
    'A barrel in the bush is worth a bird in the bucket.',
    'Two birds, two stones.',
    'Time is dollars.'
]


def activity_command( good_reads_client, user_key ):
    updates = resolve_user_activity( good_reads_client, user_key )
    total_n = min( len( updates ), DISPLAY_NUM_ACTIVITIES )
    text = f'Here are the last {total_n} updates from {user_key}:' if len( updates ) else f'This user has no activity yet.'
    for n in range( 1, total_n + 1 ):
        update = updates[ n ]
        if update[ '@type' ] == 'review':
            author = update[ 'object' ][ 'book' ][ 'authors' ][ 'author' ][ 'name' ]
            rating = update[ 'action' ][ 'rating' ]
            title = update[ 'object' ][ 'book' ][ 'title' ]
            text = text + f'\n{n}. {user_key} gave {title} by {author}: {rating} / 5 stars.' 
        elif update[ '@type' ] == 'readstatus':
            author = update[ 'object' ][ 'read_status' ][ 'review' ][ 'book' ][ 'author' ][ 'name' ]
            title = update[ 'object' ][ 'read_status' ][ 'review' ][ 'book' ][ 'title' ]
            text = text + f'\n{n}. {user_key} wants to read {title} by {author}.'
    return text


def book_command( good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        return f'{book.title} by {book.authors[ 0 ].name} has an average rating of {book.average_rating} / 5 stars.'
    else:
        return BOOK_COMMAND_ERROR


def quote_command():
    return choice( QUOTES )
 

def rating_command( good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        return f'{book.title} by {book.authors[ 0 ].name} has an average rating of {book.average_rating} / 5 stars.'
    else:
        return RATING_COMMAND_ERROR

def review_command( good_reads_client, text ):
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
        return ( f'{user.user_name} gave {book.title} by {book.authors[ 0 ].name} {rev.rating} / 5 stars.\n{user.user_name} wrote (might be cut-off): "{body}"'
                        if body else
               f'{user.user_name} gave {book.title} by {book.authors[ 0 ].name} {rev.rating} / 5 stars.' )
    except:
        return REVIEW_COMMAND_ERROR


def help_command():
    text = ''
    for key in AVAILABLE_COMMANDS:
        if len( AVAILABLE_COMMANDS[ key ][ 'args' ] ):
            text = text + '\n'.join( [ f'{key} {arg}' for arg in AVAILABLE_COMMANDS[ key ][ 'args' ] ] )
        else:
            text = text + f'{key}'
        text = text + '\n' + AVAILABLE_COMMANDS[ key ][ 'description' ] + '\n\n'
    return text
