#!/usr/bin/python3

import time
import re
import os
from datetime import datetime
import urllib.request
from urllib.error import HTTPError
from screenlogger.screenlogger import Msg


class Util:


    def __init__(self, filename, path, screenmode):
        self.msg = Msg(filename, path, screenmode)


    def goodnode(self, nodelist):
        ''' Goes through the provided list
        and returns the first server node
        that does not return an error.
        '''
        for n in nodelist:
            req = urllib.request.Request(url=n)
            try:
                self.msg.message("Trying " + n)
                urllib.request.urlopen(req)
            except HTTPError as e:
                self.msg.error_message(e)
            else:
                self.msg.message("Using " + n)
                return n


    def identifier(self, author, permlink):
        ''' Converts an author's name and permlink 
        into an identifier
        '''
        return ("@" + author + "/" + permlink)


    def permlink(self, identifier):
        ''' Deconstructs an identifier into
        an account name and permlink
        '''
        temp = identifier.split("@")
        temp2 = temp[1].split("/")
        return [temp2[0], temp2[1]]


    def days_back(self, date):
        ''' Gives a number (integer) of days
        since a given date
        '''
        daysback = (datetime.now() - datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')).days
        if daysback < 0:
            daysback = 0
        return daysback


    def scale_vote(self, value):
        ''' Scales a vote value between 1 and 100
        to 150 to 10000 as required by Steem-Python
        for certain method calls
        '''
        value = int(value) * 100
        if value < 150:
            value = 150
        if value > 10000:
            value = 10000
        return value


    def calc_regenerated(self, lastvotetime):
        ''' Uses math formula to calculate the amount
        of steem power that would have been regenerated
        given a certain datetime object
        '''
        delta = datetime.utcnow() - datetime.strptime(lastvotetime,'%Y-%m-%dT%H:%M:%S')
        td = delta.days
        ts = delta.seconds
        tt = (td * 86400) + ts
        return tt * 10000 / 86400 / 5


    def retry(self, msg, e, retry_num, waittime):
        ''' Creates the retry message and waits the 
        given default time when a method call fails
        or a server does not respond appropriately.
        '''
        self.msg.error_message(msg)
        self.msg.error_message(e)
        self.msg.error_message("Attempt number " + str(retry_num) + ". Retrying in " + str(waittime) + " seconds.")
        time.sleep(waittime)



# EOF
