#!/usr/bin/python3


from steemconnect.client import Client
from steemconnect.operations import Vote



class SteemConnect:



    def __init__(self, client_id="", client_secret="", callback_url="", permissions="login,offline,vote"):

        self.steemconnect = None

        self.client_id = client_id

        self.client_secret = client_secret

        self.callback_url = callback_url

        self.permissions = permissions



    def connect(self, accesstoken=None): 
        if accesstoken:
            self.steemconnect = Client(access_token=accesstoken)

        else:
            self.steemconnect = Client(client_id=self.client_id, client_secret=self.client_secret)



    def get_token(self, code=None):

        tokenobj = self.steemconnect.get_access_token(code)

        for t in tokenobj:

            if t == 'error':

                print (tokenobj[t])

                return False

            elif t == 'access_token':

                self.username = tokenobj['username']

                self.refresh_token = tokenobj['refresh_token']

                return tokenobj[t]



    def auth_url(self):

        return self.steemconnect.get_login_url(self.callback_url, self.permissions, "get_refresh_token=True")



    def vote(self, voter, author, permlink, voteweight):

        vote = Vote(voter, author, permlink, voteweight)

        result = self.steemconnect.broadcast([vote.to_operation_structure()])

        return result



# Run as main

if __name__ == "__main__":

    s = SteemConnect()
    s.connect()
    print(s.auth_url())


# EOF

