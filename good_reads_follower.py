from datetime import datetime, timezone
from good_reads_utilities import resolve_user_activity
from time import sleep

class FollowNode:

    def __init__( self, uid, last_update ):
        self.uid = uid
        self.last_update = last_update

    def __repr__( self ):
        return self.uid

    @property
    def last_update( self ):
        return self.last_update

    @property
    def uid( self ):
        return self.uid


class FollowManager:

    FOLLOW_INTERVAL = 60

    def __init__( self ):
        self.scanning = False
        self.follow_list = {}
    

    async def start_scan( self, command_q ):
        if self.scanning and len( self.follow_list ):
            for entry in self.follow_list:
                await command_q.run_command( self.follow_list[ 'channel' ], { 'fx': self.follow_updated_command }, entry )
            await self.start_scan( command_q )
        else:
            self.scanning = True


    def follow_command( self, channel, good_reads_client, user_key ):
        updates = resolve_user_activity( good_reads_client, user_key )
        if updates:
            last_update = datetime.fromtimestamp( datetime.strptime( updates[ 0 ][ 'updated_at' ], DATE_TIME_FORMAT ).timestamp(), tz=timezone.utc )
        else:
            last_update = datetime.now( timezone.utc ).timestamp()
        self.follow_list[ user_key ] = { 'channel': channel, 'last_update': last_update }
        return f'The {channel.name} channel on {channel.guild.name} is now following the GoodReads members {user_key}.'


    def follow_updated_command( self, channel, good_reads_client, user_key ):
        lastest = 0
        ret = "";
        for update in resolve_user_activity( self.good_reads_client, self.follow_list[ user_key ][ 'user_id' ] ):
            ts = datetime.fromtimestamp( datetime.strptime( update[ 'updated_at' ], DATE_TIME_FORMAT ).timestamp(), tz=timezone.utc )
            if self.follow_list[ user_key ][ 'last_update' ] < ts:
                author = update[ 'object' ][ 'read_status' ][ 'review' ][ 'book' ][ 'author' ][ 'name' ]
                rtype =  update[ '@type' ]
                ret = ret + update[ 'channel' ].send( f'{author} posted a {rtype}.' ) + "\n"
            if latest < ts:
                latest = ts
        self.follow_list[ user_key ][ 'last_update' ]  = latest
        return ret

