#!/usr/bin/python3

import time
import re
import os
from datetime import datetime
import urllib.request
from urllib.error import HTTPError
from screenlogger.screenlogger import Msg
from steem.amount import Amount


class Util:


    def __init__(self, filename, path, screenmode):
        self.msg = Msg(filename, path, screenmode)
        self.total_vesting_fund_steem = None
        self.total_vesting_shares = None
        self.vote_power_reserve_rate = None
        self.info = None
        self.currentnode = 0


    def current_node(self, listlength):
        newnodenumber = 0
        path = os.path.dirname(os.path.abspath(__file__)) + "/node.dat"
        try:
            with open(path, 'r') as fh:
                try:
                    self.currentnode = fh.read()
                except Exception as e:
                    self.msg.error_message(e)
                finally:
                    fh.close()
        except Exception as e:
            self.msg.error_message(e)
        if int(self.currentnode) >= int(listlength):
            self.currentnode = 0
        else:
            newnodenumber = int(self.currentnode) + 1
        with open(path, 'w+') as fh:
            try:
                fh.write(str(newnodenumber))
            except Exception as e:
                self.msg.error_message(e)
            finally:
                fh.close()
        return int(self.currentnode)


    def goodnode(self, nodelist):
        ''' Goes through the provided list
        and returns the first server node
        that does not return an error.
        '''
        l = len(nodelist)
        for n in range(self.current_node(l), l):
            self.msg.message("Trying node " + str(n) + ": " + nodelist[n])
            try:
                req = urllib.request.Request(url=nodelist[n])
                urllib.request.urlopen(req)
            except HTTPError as e:
                self.msg.error_message(e)
                self.currentnode = int(self.currentnode) + 1
            else:
                self.msg.message("Using " + nodelist[n])
                return nodelist[n]


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


    def minutes_back(self, date):
        ''' Gives a number (integer) of days
        since a given date
        '''
        elapsed = (datetime.utcnow() - datetime.strptime(date,'%Y-%m-%dT%H:%M:%S'))
        if elapsed.days > 0:
            secondsback = (elapsed.days * 24 * 60 * 60) + elapsed.seconds
        else:
            secondsback = elapsed.seconds
        minutesback = secondsback / 60
        return int(minutesback)


    def scale_vote(self, value):
        ''' Scales a vote value between 1 and 100
        to 150 to 10000 as required by Steem-Python
        for certain method calls
        '''
        value = int(value) * 100
        if value < 100:
            value = 100
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


    def steem_per_mvests(self):
        """ Obtain STEEM/MVESTS ratio
        """
        return (self.total_vesting_fund_steem /
                (self.total_vesting_shares / 1e6))


    def sp_to_vests(self, sp):
        """ Obtain VESTS (not MVESTS!) from SP
            :param number sp: SP to convert
        """
        return sp * 1e6 / self.steem_per_mvests()


    def vests_to_sp(self, vests):
        """ Obtain SP from VESTS (not MVESTS!)
            :param number vests: Vests to convert to SP
        """
        return vests / 1e6 * self.steem_per_mvests()


    def sp_to_rshares(self, sp, voting_power=10000, vote_pct=10000):
        """ Obtain the r-shares
            :param number sp: Steem Power
            :param int voting_power: voting power (100% = 10000)
            :param int vote_pct: voting participation (100% = 10000)
        """
        vesting_shares = int(self.sp_to_vests(sp) * 1e6)
        used_power = int((voting_power * vote_pct) / 10000);
        max_vote_denom = self.vote_power_reserve_rate * (5 * 60 * 60 * 24) / (60 * 60 * 24);
        used_power = int((used_power + max_vote_denom - 1) / max_vote_denom)
        rshares = ((vesting_shares * used_power) / 10000)
        return rshares


# EOF
