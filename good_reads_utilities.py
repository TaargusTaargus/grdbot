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
    )
    return response[ 'user' ][ 'updates' ][ 'update' ]
