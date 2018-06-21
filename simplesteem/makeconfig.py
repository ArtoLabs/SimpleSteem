#!/usr/bin/python3

import os

class MakeConfig:



    def setup (self):
        mainaccount = self.add_quotes(self.enter_config_value("mainaccount", 'ned'))
        keys = self.enter_config_value("keys", '[]')
        nodes = self.enter_config_value("nodes", 
                '["https://steemd.minnowsupportproject.org",'
                + '"https://steemd.privex.io","https://gtg.steem.house:8090",'
                + '"https://steemd.pevo.science","https://rpc.steemliberator.com"]')
        client_id = self.add_quotes(self.enter_config_value("client_id"))
        client_secret = self.add_quotes(self.enter_config_value("client_secret"))
        callback_url = self.add_quotes(self.enter_config_value("callback_url"))
        permissions = self.add_quotes(self.enter_config_value("permissions", "login,offline,vote"))
        logpath = self.add_quotes(self.enter_config_value("logpath", None))
        screenmode = self.add_quotes(self.enter_config_value("screenmode", "quiet"))
        self.make(mainaccount=mainaccount, keys=keys, nodes=nodes, client_id=client_id, 
            client_secret=client_secret, callback_url=callback_url, permissions=permissions,
            logpath=logpath, screenmode=screenmode)



    def add_quotes(self, value):
        return '"'+value+'"'



    def make(self, **kwargs):
        configpath = os.path.dirname(os.path.abspath(__file__)) + "/config.py"
        
        print ("Writing to " + configpath)
        with open(configpath, 'w+') as fh:
            try:
                fh.write("#!/usr/bin/python3\n\n")
            except Exception as e:
                print(e)
            else:
                for key, value in kwargs.items():
                    fh.write(key + ' = ' + value + "\n")



    def enter_config_value(self, key, default=""):
        value = input('Please enter a value for ' + key + ': ')
        if value:
            return value
        else:
            return default




# Run as main

if __name__ == "__main__":

    m = MakeConfig()




# EOF
