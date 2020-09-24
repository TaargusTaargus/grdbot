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

    def __init__( self, follow_list = [] ):
        self.follow_list = follow_list


    def check_for_updates( self ):
        for follow in self.follow_list:
            if follow.last_update 
