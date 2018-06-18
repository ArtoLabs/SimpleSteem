#!/usr/bin/python3


import time
import re
from datetime import datetime
import urllib.request
from urllib.error import HTTPError
from screenlogger.screenlogger import Msg


class Util:



    def __init__(self):
        self.msg = Msg()



    def goodnode(self, nodelist):
        for n in nodelist:
            req = urllib.request.Request(url=n)
            try:
                urllib.request.urlopen(req)
            except HTTPError as e:
                self.msg.error_message(e)
                return False
            else:
                self.msg.message("Using " + n)
                return n



    def identifier(self, author, permlink):
        return ("@" + author + "/" + permlink)



    def permlink(self, identifier):
        temp = identifier.split("@")
        temp2 = temp[1].split("/")
        return [temp2[0], temp2[1]]



    def days_back(self, date):
        return (datetime.now() - datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')).days



    def scale_vote(self, value):
        value = int(value) * 100
        if value < 150:
            value = 150
        if value > 10000:
            value = 10000
        return value



    def calc_regenerated(self, lastvotetime):
        delta = datetime.utcnow() - datetime.strptime(lastvotetime,'%Y-%m-%dT%H:%M:%S')
        td = delta.days
        ts = delta.seconds
        tt = (td * 86400) + ts
        return tt * 10000 / 86400 / 5



    def retry(self, msg, e, retry_num, waittime):
        self.msg.error_message(msg)
        self.msg.error_message(e)
        self.msg.error_message("Attempt number " + str(retry_num) + ". Retrying in " + str(waittime) + " seconds.")
        time.sleep(waittime)




# EOF
