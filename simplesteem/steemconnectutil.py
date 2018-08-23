#!/usr/bin/python3

from steemconnect.client import Client
from steemconnect.operations import Vote
from screenlogger.screenlogger import Msg


class SteemConnect:


    def __init__(self, client_id="", 
                    client_secret="", 
                    callback_url="", 
                    permissions="login,offline,vote"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url
        self.permissions = permissions
        self.sc = None
        self.accesstoken = None
        self.msg = Msg("simplesteem.log", "~", "quiet")


    def steemconnect(self, accesstoken=None):
        ''' Initializes the SteemConnect Client
        class
        '''
        if self.sc is not None:
            return self.sc
        if accesstoken is not None:
            self.accesstoken = accesstoken
        if self.accesstoken is None:
            self.sc = Client(client_id=self.client_id, 
                            client_secret=self.client_secret)
        else:
            self.sc = Client(access_token=self.accesstoken,
                            client_id=self.client_id, 
                            client_secret=self.client_secret)
        return self.sc


    def get_token(self, code=None):
        ''' Uses a SteemConnect refresh token
        to retreive an access token
        '''
        tokenobj = self.steemconnect().get_access_token(code)
        for t in tokenobj:
            if t == 'error':
                self.msg.error_message(str(tokenobj[t]))
                return False
            elif t == 'access_token':
                self.username = tokenobj['username']
                self.refresh_token = tokenobj['refresh_token']
                return tokenobj[t]


    def auth_url(self):
        ''' Returns the SteemConnect url
        used for authentication
        '''
        return self.steemconnect().get_login_url(
                            self.callback_url, 
                            self.permissions, 
                            "get_refresh_token=True")


    def vote(self, voter, author, permlink, voteweight):
        ''' Uses a SteemConnect accses token
        to vote.
        '''
        vote = Vote(voter, author, permlink, voteweight)
        result = self.steemconnect().broadcast(
            [vote.to_operation_structure()])
        return result


# Run as main

if __name__ == "__main__":

    s = SteemConnect()
    print(s.auth_url())


# EOF
