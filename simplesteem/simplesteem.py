#!/usr/bin/python3

import time
import re
import imp
import os
import json
from steem import Steem
from steem.post import Post
from steem.amount import Amount
from steem.dex import Dex
from steembase.account import PrivateKey
from screenlogger.screenlogger import Msg
from simplesteem import util
from simplesteem import makeconfig
from simplesteem import steemconnectutil
from simplesteem import default


class SimpleSteem:  


    def __init__(self, **kwargs):
        ''' Looks for config.py if not found runs
        setup which prompts user for the config values
        one time only.
        '''
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
        self.dex = None
        self.msg = Msg("simplesteem.log", 
                        self.logpath, 
                        self.screenmode)
        self.util = util.Util("simplesteem.log", 
                        self.logpath, 
                        self.screenmode)
        self.connect = steemconnectutil.SteemConnect(
                        self.client_id, 
                        self.client_secret, 
                        self.callback_url, 
                        self.permissions)
        self.checkedaccount = None
        self.accountinfo = None
        self.blognumber = 0
        self.reward_balance = 0


    def account(self, account=None):
        ''' Fetches account information and stores the
        result in a class variable. Returns that variable
        if the account has not changed.
        '''
        for num_of_retries in range(default.max_retry):
            if account is None:
                account = self.mainaccount
            if account == self.checkedaccount:
                return self.accountinfo
            self.checkedaccount = account
            try:
                self.accountinfo = self.steem_instance().get_account(account)
            except Exception as e:
                self.util.retry(("COULD NOT GET ACCOUNT INFO FOR " + str(account)), 
                    e, num_of_retries, default.wait_time)
                self.s = None
            else:
                if self.accountinfo is None:
                    self.msg.error_message("COULD NOT FIND ACCOUNT: " + str(account))
                    return False
                else:
                    return self.accountinfo


    def steem_instance(self):
        ''' Returns the steem instance if it already exists
        otherwise uses the goodnode method to fetch a node
        and instantiate the Steem class.
        '''
        if self.s:
            return self.s
        for num_of_retries in range(default.max_retry):
            node = self.util.goodnode(self.nodes)
            try:
                self.s = Steem(keys=self.keys, 
                    nodes=[node])
            except Exception as e:
                self.util.retry("COULD NOT GET STEEM INSTANCE", 
                    e, num_of_retries, default.wait_time)
                self.s = None
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
        ''' This can be used to verify either a private
        posting key or to verify a steemconnect refresh
        token and retreive the access token.
        '''
        if (re.match( r'^[A-Za-z0-9]+$', tokenkey)
                        and tokenkey is not None
                        and len(tokenkey) <= 64
                        and len(tokenkey) >= 16):
            pubkey = PrivateKey(tokenkey).pubkey or 0
            pubkey2 = self.account(acctname)
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
        ''' Fetches and returns the 3 values
        needed to calculate the reward pool
        and other associated values such as rshares.
        Returns the reward balance, all recent claims
        and the current price of steem.
        '''
        if self.reward_balance > 0:
            return self.reward_balance
        else:
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
        ''' Gets the reward pool balances
        then calculates rshares to steem
        '''
        self.reward_pool_balances()
        return round(
            rshares 
            * self.reward_balance 
            / self.recent_claims 
            * self.base, 4)


    def global_props(self):
        ''' Retrieves the global properties
        used to determine rates used for calculations
        in converting steempower to vests etc.
        Stores these in the Utilities class as that
        is where the conversions take place, however
        SimpleSteem is the class that contains
        steem_instance, so to to preserve heirarchy 
        and to avoid "spaghetti code", this method
        exists in this class.
        '''
        if self.util.info is None:
            self.util.info = self.steem_instance().get_dynamic_global_properties()
            self.util.total_vesting_fund_steem = Amount(self.util.info["total_vesting_fund_steem"]).amount
            self.util.total_vesting_shares = Amount(self.util.info["total_vesting_shares"]).amount
            self.util.vote_power_reserve_rate = self.util.info["vote_power_reserve_rate"]
        return self.util.info


    def current_vote_value(self, **kwargs):
        ''' Ensures the needed variables are
        created and set to defaults although
        a variable number of variables are given.
        '''
        try:
            kwargs.items()
        except:
            pass
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)
        try:
            self.lastvotetime
        except:
            self.lastvotetime=None
        try:
            self.steempower
        except:
            self.steempower=0
        try:
            self.voteweight
        except:
            self.voteweight=100
        try:
            self.votepoweroverride
        except:
            self.votepoweroverride=0
        try:
            self.accountname
        except:
            self.accountname=None              
        if self.accountname is None:
            self.accountname = self.mainaccount   
        if self.check_balances(self.accountname) is not False:
            if self.voteweight > 0 and self.voteweight < 101:
                self.voteweight = self.util.scale_vote(self.voteweight)
            if self.votepoweroverride > 0 and self.votepoweroverride < 101:
                self.votepoweroverride = self.util.scale_vote(self.votepoweroverride) 
            else:
                self.votepoweroverride = (self.votepower 
                                + self.util.calc_regenerated(
                                self.lastvotetime))
            self.vpow = round(self.votepoweroverride / 100, 2)
            self.global_props()
            self.rshares = self.util.sp_to_rshares(self.steempower, 
                                            self.votepoweroverride, 
                                            self.voteweight)
            self.votevalue = self.rshares_to_steem(self.rshares)
            return self.votevalue
        return None


    def check_balances(self, account=None):
        ''' Fetches an account balance and makes
        necessary conversions
        '''
        a = self.account(account)
        if a is not False and a is not None:
            self.sbdbal = Amount(a['sbd_balance']).amount
            self.steembal = Amount(a['balance']).amount
            self.votepower = a['voting_power']
            self.lastvotetime = a['last_vote_time']
            vs = Amount(a['vesting_shares']).amount
            dvests = Amount(a['delegated_vesting_shares']).amount
            rvests = Amount(a['received_vesting_shares']).amount
            vests = (float(vs) - float(dvests)) + float(rvests)
            try:
                self.global_props()
                self.steempower_delegated = self.util.vests_to_sp(dvests)
                self.steempower_raw = self.util.vests_to_sp(vs)
                self.steempower = self.util.vests_to_sp(vests)
            except Exception as e:
                self.msg.error_message(e)
            else:
                return [self.sbdbal, self.steembal, self.steempower, 
                        self.votepower, self.lastvotetime]
        return False


    def transfer_funds(self, to, amount, denom, msg):
        ''' Transfer SBD or STEEM to the given account
        '''
        try:
            self.steem_instance().commit.transfer(to, 
                float(amount), denom, msg, self.mainaccount)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return True


    def get_my_history(self, account=None, limit=10000):
        ''' Fetches the account history from
        most recent back
        '''
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
        ''' Used for creating a main post
        to an account's blog. Waits 20 seconds
        after posting as that is the required 
        amount of time between posting.
        '''
        for num_of_retries in range(default.max_retry):
            try:
                self.msg.message("Attempting to post " + permlink)
                self.steem_instance().post(title, 
                                            body, 
                                            self.mainaccount, 
                                            permlink, 
                                            None, None, None, None, 
                                            tags, None, False)   
            except Exception as e:
                self.util.retry("COULD NOT POST '" + title + "'", 
                    e, num_of_retries, 10)
                self.s = None
            else:
                self.msg.message("Post seems successful. Wating 60 seconds before verifying...")
                self.s = None
                time.sleep(60)
                checkident = self.recent_post()
                ident = self.util.identifier(self.mainaccount, permlink)
                if checkident == ident:
                    return True
                else:
                    self.util.retry('A POST JUST CREATED WAS NOT FOUND IN THE '
                                    + 'BLOCKCHAIN {}'''.format(title), 
                                    "Identifiers do not match", 
                                    num_of_retries, default.wait_time)
                    self.s = None


    def reply(self, permlink, msgbody):
        ''' Used for creating a reply to a 
        post. Waits 20 seconds
        after posting as that is the required 
        amount of time between posting.
        '''
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
                self.s = None
            else:
                self.msg.message("Replied to " + permlink)
                time.sleep(20)
                return True


    def follow(self, author):
        ''' Follows the given account
        '''
        try:
            self.steem_instance().commit.follow(author, 
                ['blog'], self.mainaccount)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return True


    def unfollow(self, author):
        ''' Unfollows the given account
        '''
        try:
            self.steem_instance().commit.unfollow(author, 
                ['blog'], self.mainaccount)
        except Exception as e:
            self.msg.error_message(e)
            return False
        else:
            return True


    def following(self, account=None, limit=100):
        ''' Gets a list of all the followers
        of a given account. If no account is given
        the followers of the mainaccount are
        returned.
        '''
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


    def recent_post(self, author=None, daysback=0, flag=0):
        ''' Returns the most recent post from the account
        given. If the days back is greater than zero
        then the most recent post is returned for that
        day. For instance if daysback is set to 2
        then it will be the most recent post from 2 days
        ago (48 hours).
        '''
        if not author:
            author = self.mainaccount
        for num_of_retries in range(default.max_retry):
            try:
                self.blog = self.steem_instance().get_blog(author, 0, 30)
            except Exception as e:
                self.util.retry('COULD NOT GET THE '
                                + 'MOST RECENT POST FOR '
                                + '{}'.format(author), 
                                e, num_of_retries, default.wait_time)
                self.s = None
            else:
                i = 0
                for p in self.blog:
                    if p['comment']['author'] == author:
                        self.blognumber = i
                        ageinminutes = self.util.minutes_back(p['comment']['created'])
                        ageindays = (ageinminutes / 60) / 24
                        if (int(ageindays) == daysback):
                            if flag == 1 and ageinminutes < 15:
                                return None
                            else:
                                return self.util.identifier(
                                    p['comment']['author'],
                                    p['comment']['permlink'])
                        else:
                            return None
                    i += 1


    def vote_history(self, permlink, author=None):
        ''' Returns the raw vote history of a
        given post from a given account
        '''
        if author is None:
            author = self.mainaccount
        return self.steem_instance().get_active_votes(author, permlink)


    def vote(self, identifier, weight=100.0):
        ''' Waits 5 seconds as that is the required amount 
        of time between votes.
        '''
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
                    self.s = None
            else:
                return True


    def resteem(self, identifier):
        ''' Waits 20 seconds as that is the required 
        amount of time between resteems
        '''
        for num_of_retries in range(default.max_retry):
            try:
                self.steem_instance().resteem(
                    identifier, self.mainaccount)
                self.msg.message("resteemed " + identifier)
                time.sleep(10)
            except Exception as e:
                self.util.retry('''COULD NOT RESTEEM 
                                {}'''.format(identifier), 
                                e, num_of_retries, default.wait_time)
                self.s = None
            else:
                return True


    def dex_ticker(self):
        ''' Simply grabs the ticker using the 
        steem_instance method and adds it
        to a class variable.
        '''
        self.dex = Dex(self.steem_instance())
        self.ticker = self.dex.get_ticker();
        return self.ticker


    def steem_to_sbd(self, steemamt=0, price=0, account=None):
        ''' Uses the ticker to get the highest bid
        and moves the steem at that price.
        '''
        if not account:
            account = self.mainaccount
        if self.check_balances(account):
            if steemamt == 0:
                steemamt = self.steembal
            elif steemamt > self.steembal:
                self.msg.error_message("INSUFFICIENT FUNDS. CURRENT STEEM BAL: " 
                                        + str(self.steembal))
                return False
            if price == 0:
                price = self.dex_ticker()['highest_bid']
            try:
                self.dex.sell(steemamt, "STEEM", price, account=account)
            except Exception as e:
                self.msg.error_message("COULD NOT SELL STEEM FOR SBD: " + str(e))
                return False
            else:
                self.msg.message("TRANSFERED " 
                                    + str(steemamt) 
                                    + " STEEM TO SBD AT THE PRICE OF: $"
                                    + str(price))
                return True
        else:
            return False


    def sbd_to_steem(self, sbd=0, price=0, account=None):
        ''' Uses the ticker to get the lowest ask
        and moves the sbd at that price.
        '''
        if not account:
            account = self.mainaccount
        if self.check_balances(account):
            if sbd == 0:
                sbd = self.sbdbal
            elif sbd > self.sbdbal:
                self.msg.error_message("INSUFFICIENT FUNDS. CURRENT SBD BAL: " 
                                        + str(self.sbdbal))
                return False
            if price == 0:
                price = 1 / self.dex_ticker()['lowest_ask']
            try:
                self.dex.sell(sbd, "SBD", price, account=account)
            except Exception as e:
                self.msg.error_message("COULD NOT SELL SBD FOR STEEM: " + str(e))
                return False
            else:
                self.msg.message("TRANSFERED " 
                                    + str(sbd) 
                                    + " SBD TO STEEM AT THE PRICE OF: $"
                                    + str(price))
                return True
        else:
            return False


    def vote_witness(self, witness, account=None):
        ''' Uses the steem_instance method to
        vote on a witness.
        '''
        if not account:
            account = self.mainaccount
        try:
            self.steem_instance().approve_witness(witness, account=account)
        except Exception as e:
            self.msg.error_message("COULD NOT VOTE " 
                                    + witness + " AS WITNESS: " + e)
            return False
        else:
            return True


    def unvote_witness(self, witness, account=None):
        ''' Uses the steem_instance method to
        unvote a witness.
        '''
        if not account:
            account = self.mainaccount
        try:
            self.steem_instance().disapprove_witness(witness, account=account)
        except Exception as e:
            self.msg.error_message("COULD NOT UNVOTE " 
                                    + witness + " AS WITNESS: " + e)
            return False
        else:
            return True


    def voted_me_witness(self, account=None, limit=100):
        ''' Fetches all those a given account is
        following and sees if they have voted that
        account as witness.
        '''
        if not account:
            account = self.mainaccount
        self.has_voted = []
        self.has_not_voted = []
        following = self.following(account, limit)
        for f in following:
            wv = self.account(f)['witness_votes']
            voted = False
            for w in wv:
                if w == account:
                    self.has_voted.append(f)
                    voted = True
            if not voted:
                self.has_not_voted.append(f)
        return self.has_voted


    def muted_me(self, account=None, limit=100):
        ''' Fetches all those a given account is
        following and sees if they have muted that
        account.
        '''
        self.has_muted = []
        if account is None:
            account = self.mainaccount
        following = self.following(account, limit)
        if following is False:
            self.msg.error_message("COULD NOT GET FOLLOWING FOR MUTED")
            return False
        for f in following:
            h = self.get_my_history(f)
            for a in h:
                if a[1]['op'][0] == "custom_json":
                    j = a[1]['op'][1]['json']
                    d = json.loads(j)
                    try:
                        d[1]
                    except:
                        pass
                    else:
                        for i in d[1]:
                            if i == "what":
                                if len(d[1]['what']) > 0:
                                    if d[1]['what'][0] == "ignore":
                                        if d[1]['follower'] == account:
                                            self.msg.message("MUTED BY " + f)
                                            self.has_muted.append(f)
        return self.has_muted


    def delegate(self, to, steempower):
        ''' Delegates based on Steem Power rather
        than by vests.
        '''
        self.global_props()
        vests = self.util.sp_to_vests(steempower)
        strvests = str(vests)
        strvests = strvests + " VESTS"
        try:
            self.steem_instance().commit.delegate_vesting_shares(to, 
                                                                strvests, 
                                                                account=self.mainaccount)
        except Exception as e:
            self.msg.error_message("COULD NOT DELEGATE " 
                                    + str(steempower) + " SP TO " 
                                    + to + ": " + str(e))
            return False
        else:
            self.msg.message("DELEGATED " + str(steempower) + " STEEM POWER TO " + str(to))
            return True


# EOF
