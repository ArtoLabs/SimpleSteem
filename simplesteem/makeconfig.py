#!/usr/bin/python3



class MakeConfig:



    def setup (self):
        mainaccount = self.add_quotes(self.enter_config_value("mainaccount", '"ned"'))
        keys = self.enter_config_value("keys", '[]')
        nodes = self.enter_config_value("nodes", '["https://steemd.minnowsupportproject.org",'
                                        + '"https://steemd.privex.io","https://gtg.steem.house:8090",'
                                        + '"https://steemd.pevo.science","https://rpc.steemliberator.com"]')
        client_id = self.add_quotes(self.enter_config_value("client_id"))
        client_secret = self.add_quotes(self.enter_config_value("client_secret"))
        callback_url = self.add_quotes(self.enter_config_value("callback_url"))
        permissions = self.add_quotes(self.enter_config_value("permissions", "login,offline,vote"))
        self.make(mainaccount=mainaccount, keys=keys, nodes=nodes, client_id=client_id, 
            client_secret=client_secret, callback_url=callback_url, permissions=permissions)



    def add_quotes(self, value):
        return '"'+value+'"'



    def make(self, **kwargs):
        config_file = open('config.py', 'w')
        config_file.write("#!/usr/bin/python3\n\n")
        for key, value in kwargs.items():
            config_file.write(key + ' = ' + value + "\n")



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
