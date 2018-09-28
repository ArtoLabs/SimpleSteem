#!/usr/bin/python3

import os

class MakeConfig:


    def setup (self):
        ''' Runs only the first time SimpleSteem() 
        is instantiated. Prompts user for the values
        that are then written to config.py
        '''
        mainaccount = self.add_quotes(self.enter_config_value("mainaccount", 'ned'))
        keys = self.enter_config_value("keys", '[]')
        nodes = self.enter_config_value("nodes", 
                '["https://steemd.minnowsupportproject.org",'
                + '"https://rpc.buildteam.io",'
                + '"https://rpc.curiesteem.com",'
                + '"https://gtg.steem.house:8090",'
                + '"https://rpc.steemliberator.com",'
                + '"https://rpc.steemviz.com",'
                + '"https://steemd.privex.io"]')
        client_id = self.add_quotes(self.enter_config_value("client_id"))
        client_secret = self.add_quotes(self.enter_config_value("client_secret"))
        callback_url = self.add_quotes(self.enter_config_value("callback_url"))
        permissions = self.add_quotes(self.enter_config_value("permissions", "login,offline,vote"))
        logpath = self.add_quotes(self.enter_config_value("logpath", ""))
        screenmode = self.add_quotes(self.enter_config_value("screenmode", "quiet"))
        self.make(mainaccount=mainaccount, keys=keys, nodes=nodes, client_id=client_id, 
            client_secret=client_secret, callback_url=callback_url, permissions=permissions,
            logpath=logpath, screenmode=screenmode)


    def add_quotes(self, value):
        return '"'+str(value)+'"'


    def make(self, **kwargs):
        ''' takes the arguments and writes them as 
        variable / value pairs to config.py
        '''
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
        ''' Prompts user for a value
        '''
        value = input('Please enter a value for ' + key + ': ')
        if value:
            return value
        else:
            return default


# Run as main
if __name__ == "__main__":
    m = MakeConfig()


# EOF
