from asyncio import sleep
from datetime import datetime, timezone
from json import dumps, load
from good_reads_utilities import resolve_user_activity, resolve_update_embed
DATE_TIME_FORMAT = '%a, %d %b %Y %H:%M:%S %z'

class FollowManager:

    FOLLOW_INTERVAL = 5

    def __init__( self ):
        self.follow_list = {}
        self.scanning = False


    def __load_followers_list__( self, file_path ):
        try:
            with open( file_path, 'r+' ) as f:
                self.follow_list = load( f )
        except:
            return


    def __write_followers_list__( self, file_path ):
        with open( file_path, 'w' ) as f:
            json_string = dumps( self.follow_list, indent=4 )
            f.write( json_string )


    async def start_scan( self, command_q, channels, file_path ):
        self.__load_followers_list__( file_path )
        self.scanning = True
        while self.scanning:
            for entry in self.follow_list:
                await command_q.run_command(
                    channels[ self.follow_list[ entry ][ 'channel_id' ] ],
                    { 'fx': self.follow_updated_command },
                    self.follow_list[ entry ][ 'user_id' ]
                )

            self.__write_followers_list__( file_path )

            await sleep( self.FOLLOW_INTERVAL )


    async def follow_command( self, channel, good_reads_client, user_key ):
        updates = resolve_user_activity( good_reads_client, user_key )
        if updates:
            last_update = datetime.fromtimestamp( datetime.strptime( updates[ 0 ][ 'updated_at' ], DATE_TIME_FORMAT ).timestamp(), tz=timezone.utc ).timestamp()
        else:
            last_update = datetime.now( timezone.utc ).timestamp()
        self.follow_list[ user_key + ":" + str( channel.id ) ] = { 'channel_id': channel.id, 'last_update': last_update, 'user_id': user_key }
        await channel.send( f'The {channel.name} channel on {channel.guild.name} is now following the GoodReads members {user_key}.' )


    async def follow_updated_command( self, channel, good_reads_client, user_key ):
        key = user_key + ":" + str( channel.id )
        latest = 0
        ret = "";
        for update in resolve_user_activity( good_reads_client, user_key ):
            ts = datetime.fromtimestamp( datetime.strptime( update[ 'updated_at' ], DATE_TIME_FORMAT ).timestamp(), tz=timezone.utc ).timestamp()
            if self.follow_list[ key ][ 'last_update' ] < ts:
                await channel.send( embed = resolve_update_embed( user_key, update ) )
            if latest < ts:
                latest = ts
        self.follow_list[ key ][ 'last_update' ] = latest
        


