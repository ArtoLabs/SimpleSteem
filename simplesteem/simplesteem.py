#!/usr/bin/python3

import time
import re
import imp
import os
from steem import Steem
from steem.post import Post
from steem.amount import Amount
from steem.converter import Converter
from steembase.account import PrivateKey
from screenlogger.screenlogger import Msg
from simplesteem import util
from simplesteem import makeconfig
from simplesteem import steemconnectutil
from simplesteem import default


class SimpleSteem:  



    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        try:
            imp.find_module('config', 
                [os.path.dirname(os.path.realpath(__file__))])
        except ImportError:
            makeconfig.MakeConfig().setup()
        from simplesteem import config
        try:
            self.mainaccount
        except:
            self.mainaccount = config.mainaccount
        try:
            self.keys
        except:
            self.keys = config.keys
        try:
            self.nodes
        except:
            self.nodes = config.nodes
        try:
            self.client_id
        except:
            self.client_id = config.client_id
        try:
            self.client_secret
        except:
            self.client_secret = config.client_secret
        try:
            self.callback_url
        except:
            self.callback_url = config.callback_url
        try:
            self.permissions
        except:
            self.permissions = config.permissions
        try:
            self.logpath
        except:
            self.logpath = config.logpath
        try:
            self.screenmode
        except:
            self.screenmode = config.screenmode
        self.s = None
        self.c = None
        self.msg = Msg("simplesteem.log", 
                        self.logpath, 
                        self.screenmode)
        self.util = util.Util()
        self.connect = steemconnectutil.SteemConnect(
                        self.client_id, 
                        self.client_secret, 
                        self.callback_url, 
                        self.permissions)



    def steem_instance(self):
        if self.s:
            return self.s
        for x in range(default.max_retry):
            try:
                self.s = Steem(keys=self.keys, 
                    nodes=[self.util.goodnode(self.nodes)])
            except Exception as e:
                self.util.retry("COULD NOT GET STEEM INSTANCE", 
                    e, num_of_retries, default.wait_time)
            else:
                return self.s
        return False



    def claim_rewards(self):
        if self.steem_instance().claim_reward_balance(
                account=self.mainaccount):
            time.sleep(5)
            return True
        else:
            return False



    def verify_key (self, acctname=None, tokenkey=None):
        if (re.match( r'^[A-Za-z0-9]+$', tokenkey)
                        and tokenkey is not None
                        and len(tokenkey) <= 64
                        and len(tokenkey) >= 16):
            pubkey = PrivateKey(tokenkey).pubkey or 0
            pubkey2 = self.steem_instance().get_account(acctname)
            if (str(pubkey) 
                    == str(pubkey2['posting']['key_auths'][0][0])):
                self.privatekey = tokenkey
                self.refreshtoken = None
                self.accesstoken = None
                return True
            else:
                return False
        elif (re.match( r'^[A-Za-z0-9\-\_\.]+$', tokenkey)
                        and tokenkey is not None
                        and len(tokenkey) > 64):
            self.privatekey = None
            self.accesstoken = self.connect.get_token(tokenkey)
            if self.accesstoken:
                self.username = self.connect.username
                self.refreshtoken = self.connect.refresh_token
                return True
            else:
                return False
        else:
            return False



    def reward_pool_balances(self):
        try:
            self.reward_balance
        except:
            reward_fund = self.steem_instance().get_reward_fund()
            self.reward_balance = Amount(
                reward_fund["reward_balance"]).amount
            self.recent_claims = float(reward_fund["recent_claims"])
            self.base = Amount(
                self.steem_instance(
                ).get_current_median_history_price()["base"]
                ).amount
        return [self.reward_balance, self.recent_claims, self.base]



    def rshares_to_steem (self, rshares):
        self.reward_pool_balances()
        return round(
            rshares 
            * self.reward_balance 
            / self.recent_claims 
            * self.base, 4)



    def current_vote_value(self, lastvotetime=None, 
            steempower=0, voteweight=100, votepower=0):
        c = Converter()
        voteweight = self.util.scale_vote(voteweight)
        if votepower > 0 and votepower < 101:
            votepower = self.util.scale_vote(votepower) 
        else:
            votepower = votepower + self.util.calc_regenerated(lastvotetime)
        self.votepower = round(votepower / 100, 2)
        self.rshares = c.sp_to_rshares(steempower, votepower, voteweight)
        return self.rshares_to_steem(self.rshares)



    def check_balances(self, account=None):
        if not account:
            account = self.mainaccount
        try:
            acct = self.steem_instance().get_account(account)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            c = Converter()
            self.sbdbal = Amount(acct['sbd_balance']).amount or 0
            self.steembal = Amount(acct['balance']).amount or 0
            self.votepower = acct['voting_power']
            self.lastvotetime = acct['last_vote_time']
            vs = Amount(acct['vesting_shares']).amount
            dvests = Amount(acct['delegated_vesting_shares']).amount
            rvests = Amount(acct['received_vesting_shares']).amount
            vests = (float(vs) - float(dvests)) + float(rvests) 
            self.steempower = c.vests_to_sp(vests) or 0
            time.sleep(5)
            return [self.sbdbal, self.steembal, self.steempower, 
                    self.votepower, self.lastvotetime]



    def transfer_funds(self, to, amount, denom, msg):
        try:
            self.steem_instance().commit.transfer(to, 
                float(amount), denom, msg, self.mainaccount)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return True



    def get_my_history(self, account=None, limit=100):
        if not account:
            account = self.mainaccount
        try:
            h = self.steem_instance().get_account_history(
                account, -1, limit)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return h



    def post(self, title, body, permlink, tags):
        for num_of_retries in range(default.max_retry):
            try:
                self.steem_instance().post(title, 
                                            body, 
                                            self.mainaccount, 
                                            permlink, 
                                            None, None, None, None, 
                                            tags, None, True)   
            except Exception as e:
                self.util.retry("COULD NOT POST '" + title + "'", 
                    e, num_of_retries, 10)
            else:
                time.sleep(60)
                checkident = self.recent_post()
                ident = self.util.identifier(self.mainaccount, permlink)
                if checkident == ident:
                    return True
                else:
                    self.util.retry('''A POST JUST CREATED 
                                    WAS NOT FOUND IN THE 
                                    BLOCKCHAIN {}'''.format(title), 
                                    e, num_of_retries, default.wait_time)



    def reply(self, permlink, msgbody):
        for num_of_retries in range(default.max_retry): 
            try:
                self.steem_instance().post("message", 
                                            msgbody, 
                                            self.mainaccount, 
                                            None, 
                                            permlink, 
                                            None, None, "", 
                                            None, None, False)
            except Exception as e:
                self.util.retry("COULD NOT REPLY TO " + permlink, 
                    e, num_of_retries, default.wait_time)
            else:
                self.msg.message("Replied to " + permlink)
                time.sleep(20)
                return True



    def follow(self, author):
        try:
            self.steem_instance().commit.follow(author, 
                ['blog'], self.mainaccount)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return True



    def unfollow(self, author):
        try:
            self.steem_instance().commit.unfollow(author, 
                ['blog'], self.mainaccount)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return True



    def following(self, account=None, limit=100):
        if not account:
            account = self.mainaccount
        followingnames = []
        try:
            self.followed = self.steem_instance().get_following(account, 
                '', 'blog', limit)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            for a in self.followed:
                followingnames.append(a['following'])
            return followingnames



    def recent_post(self, author=None, daysback=0):
        if not author:
            author = self.mainaccount
        for num_of_retries in range(default.max_retry):
            try:
                self.blog = self.steem_instance().get_blog(author, 0, 30)
            except Exception as e:
                self.util.retry('''COULD NOT GET THE 
                                MOST RECENT POST FOR 
                                {}'''.format(author), 
                                e, num_of_retries, default.wait_time)
            else:
                for p in self.blog:
                    age = self.util.days_back(p['comment']['created'])
                    if age < 0:
                        age = 0
                    if (p['comment']['author'] == author 
                                and age == daysback):
                        return self.util.identifier(
                            p['comment']['author'], 
                            p['comment']['permlink'])



    def vote_history(self, permlink, author=None):
        if not author:
            author = self.mainaccount
        return self.steem_instance().get_active_votes(author, permlink)



    def vote(self, identifier, weight=100.0):
        for num_of_retries in range(default.max_retry):
            try:
                self.steem_instance().vote(identifier, 
                    weight, self.mainaccount)
                self.msg.message("voted for " + identifier)
                time.sleep(5)
            except Exception as e:
                if re.search(r'You have already voted in a similar way', str(e)):
                    self.msg.error_message('''Already voted on 
                                        {}'''.format(identifier))
                    return "already voted"
                else:
                    self.util.retry('''COULD NOT VOTE ON 
                                    {}'''.format(identifier), 
                                    e, num_of_retries, default.wait_time)
            else:
                return True



    def resteem(self, identifier):
        for num_of_retries in range(default.max_retry):
            try:
                self.steem_instance().resteem(
                    identifier, self.mainaccount)
                self.msg.message("resteemed " + identifier)
                time.sleep(20)
            except Exception as e:
                self.util.retry('''COULD NOT RESTEEM 
                                {}'''.format(identifier), 
                                e, num_of_retries, default.wait_time)
            else:
                return True



# EOF
