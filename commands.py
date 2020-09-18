from goodreads import review
from random import choice

AVAILABLE_COMMANDS = {
    '\\book': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return book title, author, and description based on id or book name from the GoodReads website.',
        'fx': lambda good_reads_client, text: book_command( good_reads_client, text )
    },
    '\\help': {
        'args': [],
        'description': 'Will return help text with usage information.',
        'fx': lambda good_reads_client, text: help_command()
    },
    '\\quote': {
        'args': [],
        'description': 'Will return an inspiring quote.',
        'fx': lambda good_reads_client, text: quote_command()
    },
    '\\rating': {
        'args': [ '[book-id]', '[book-name]' ],
        'description': 'Will return the rating for the book with author and title.',
        'fx': lambda good_reads_client, text: rating_command( good_reads_client, text )
    },
    '\\review': {
        'args': [ '[username] [book-id]', '[username] [book-name]' ],
        'description': 'Will return most recent review from user.',
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

def resolve_book( good_reads_client, text ):
    book = None
    try:
        book = good_reads_client.book( int( text ) )
    except ValueError:
        book = good_reads_client.search_books( text )[ 0 ]
    return book


def resolve_user( good_reads_client, text ):
    user = None
    try:
        user = good_reads_client.user( user_id = int( text ) )
    except ValueError:
        user = good_reads_client.user( username = text )
    return user

def book_command( good_reads_client,text ):
    book = resolve_book( good_reads_client, text )
    if book:
        return f'{book.title} by {book.authors[ 0 ].name} has an average rating of {book.average_rating} / 5 stars.'
    else:
        return f'Was unable to find a matching book.'


def quote_command():
    return choice( obj )
 

def rating_command( good_reads_client, text ):
    book = resolve_book( good_reads_client, text )
    if book:
        return f'{book.title} by {book.authors[ 0 ].name} has an average rating of {book.average_rating} / 5 stars.'
    else:
        return 'Unable to fetch rating for this book.'


def review_command( good_reads_client, text ):
    text = text.split()
    book = resolve_book( good_reads_client, " ".join( text[ 1: ] ) )
    user = resolve_user( good_reads_client, text[ 0 ] )
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
        return f'Unable to find a review of {book.title} by {book.authors[ 0 ].name} written by {user.user_name}.'


def help_command():
    text = ''
    for key in AVAILABLE_COMMANDS:
        if len( AVAILABLE_COMMANDS[ key ][ 'args' ] ):
            text = text + '\n'.join( [ f'{key} {arg}' for arg in AVAILABLE_COMMANDS[ key ][ 'args' ] ] )
        else:
            text = text + f'{key}'
        text = text + '\n' + AVAILABLE_COMMANDS[ key ][ 'description' ] + '\n\n'
    return text
