from discord import Embed

def resolve_book( good_reads_client, book_key ):
    book = None
    try:
        book = good_reads_client.book( int( book_key ) )
    except ValueError:
        book = good_reads_client.search_books( book_key )[ 0 ]
    return book


def resolve_user( good_reads_client, user_key ):
    user = None
    try:
        user = good_reads_client.user( user_id = int( user_key ) )
    except ValueError:
        user = good_reads_client.user( username = user_key )
    return user


def resolve_user_activity( good_reads_client, user_key ):
    user = resolve_user( good_reads_client, user_key )
    response = good_reads_client.request( 
        '/user/show.xml',
        { 'id': user.gid }
    )[ 'user' ][ 'updates' ]
    if 'update' in response:
        if '@type' in response[ 'update' ]:
            return [ response[ 'update' ] ]
        else:
            return response[ 'update' ]
    else:
            None

def resolve_update_embed( user_key, update ):
    embed = Embed()
    embed.url = update[ 'link' ]
    embed.set_image( url = update[ 'image_url' ] )
    embed.set_footer( text = 'Posted on: ' + update[ 'updated_at' ]  )
    if update[ '@type' ] == 'review':
        author = update[ 'object' ][ 'book' ][ 'authors' ][ 'author' ][ 'name' ]
        body = update[ 'body' ] + ( '' if update[ 'body' ].strip()[ -1 ] in '.!?' else '...' ) if 'body' in update else None
        rating = update[ 'action' ][ 'rating' ]
        title = update[ 'object' ][ 'book' ][ 'title' ]
        embed.title = f"{user_key}'s review of {title} by {author}"
        embed.description =  f'{rating}/5' + ( f': {body}' if body else '' )
    elif update[ '@type' ] == 'readstatus':
        author = update[ 'object' ][ 'read_status' ][ 'review' ][ 'book' ][ 'author' ][ 'name' ]
        title = update[ 'object' ][ 'read_status' ][ 'review' ][ 'book' ][ 'title' ]
        embed.description = f'{user_key} wants to read {title} by {author}'
    else:
        utype = update[ '@type' ]
        embed.description = f'GoodReads user {user_key} posted a {utype}'
    return embed 


