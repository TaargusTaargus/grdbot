from asyncio import sleep
from datetime import datetime, timezone
from good_reads_utilities import resolve_user_activity, resolve_update_message

DATE_TIME_FORMAT = '%a, %d %b %Y %H:%M:%S %z'


class FollowManager:

    FOLLOW_INTERVAL = 5

    def __init__( self ):
        self.follow_list = {}
        self.scanning = False
    

    async def start_scan( self, command_q ):
        self.scanning = True
        while self.scanning:
            for entry in self.follow_list:
                await command_q.run_command( self.follow_list[ entry ][ 'channel' ], { 'fx': self.follow_updated_command }, entry )
            await sleep( self.FOLLOW_INTERVAL )
            await self.start_scan( command_q )


    def follow_command( self, channel, good_reads_client, user_key ):
        updates = resolve_user_activity( good_reads_client, user_key )
        if updates:
            last_update = datetime.fromtimestamp( datetime.strptime( updates[ 0 ][ 'updated_at' ], DATE_TIME_FORMAT ).timestamp(), tz=timezone.utc ).timestamp()
        else:
            last_update = datetime.now( timezone.utc ).timestamp()
        self.follow_list[ user_key ] = { 'channel': channel, 'last_update': last_update }
        return f'The {channel.name} channel on {channel.guild.name} is now following the GoodReads members {user_key}.'


    def follow_updated_command( self, channel, good_reads_client, user_key ):
        latest = 0
        ret = "";
        for update in resolve_user_activity( good_reads_client, user_key ):
            ts = datetime.fromtimestamp( datetime.strptime( update[ 'updated_at' ], DATE_TIME_FORMAT ).timestamp(), tz=timezone.utc ).timestamp()
            if self.follow_list[ user_key ][ 'last_update' ] < ts:
                ret = ret + resolve_update_message( user_key, update ) + '\n'
            if latest < ts:
                latest = ts
        self.follow_list[ user_key ][ 'last_update' ]  = latest
        return ret

