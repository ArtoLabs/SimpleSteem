# SimpleSteem
A robust and reliable wrapper that dramatically simplifies the steem-python interface, expands functionality, and enables code that is gentle on public steem node servers.

# Dependencies

SimpleSteem uses the [Steem-Python library](https://github.com/steemit/steem-python), the [SteemConnect python library](https://github.com/emre/steemconnect-python-client) by [emre](https://github.com/emre), and [ScreenLogger](https://github.com/artolabs/screenlogger), a very simple class for logging what's printed to screen. All of these are automatically installed if using pip3.

# Use

There are two ways to instatiate the SimpleSteem Class. The first is to use the main account stored in the config.py file as created by the makeconfig.py module. Please see the installation instructions for more information on setting up the config.py file. To use the main account instatiate the class with no additional arguments. You may override any of the SimpleSteem method arguments.

```
from simplesteem.simplesteem import SimpleSteem
steem = SimpleSteem()
```



To instatiate SimpleSteem with your own arguments, add any of these arguments in any order. The main account must match the keys provided.

```
steem = SimpleSteem(mainaccount="yoursteemitaccount",
                    keys=['XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                        'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'],
                    nodes=['https://some.steemd.publicnode'],
                    clientid="yoursteemconnect.app",
                    clientsecret="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    callbackurl="https://yoursteemconnectapp.com",
                    permissions="login,vote,offline",
                    logpath="/var/log",
                    screenmode="quiet")
```

### steem_instance

The **steem_instance** method in the SimpleSteem class is at the heart of how simplesteem works to ensure a robust connection while being gentle on steemd public nodes. Since too many calls to a public server could be interpreted as a ddos attack, the steem_instance method as well as most of the rest of the SimpleSteem class methods use python's built in time module to wait for a certain duration in seconds between server calls. Although this may cause an app to run more slowly, it makes the app much friendlier to the public server. This can help a developer work on their app and learn the technology using public nodes before advancing to using their own node. SimpleSteem can then be converted to eliminate certain time limits, however the steem blockchain itself imposes it's own time restrictions betwen posts and voting and other such actions.

All of steem-pythons methods are inherited by SimpleSteem and can be accessed through **steem_instance**. For example:

```
steem.steem_instance().get_account()
```


### vote_history

Returns a dict of the details of the active voters of a particular post or comment as given by the argument **permlink** and **author** which both must be provided.

``` 
history = steem.vote_history(permlink, author=None)
returns dict
```


### vote

Causes **steem.mainaccount** to vote on the post or comment given as the argument **identifier** along with a vote weight between 1 and 100.

```
steem.vote(identifier, weight=100.0)
returns boolean
```


### resteem

Causes **steem.mainaccount** to resteem the post or comment given as the identifier.

```
steem.resteem(identifier)
returns boolean
```


### claim_rewards

One of the simplest methods to use. Simply claims all the rewards of **steem.mainaccount** using the keys provided in **steem.keys** (Private Posting Key must be provided).


```
steem.claim_rewards()
returns boolean
```


### verify_key

Verifies either a Steemit Private Posting Key, or a SteemConnect refresh_token belongs to the account.


```
steem.verify_key (acctname=None, tokenkey=None)
returns boolean
```


### reward_pool\_balances

Returns a list with the total reward balance, the total number of claims, and the price of steem used for making calculations based on the reward pool.


```
pool = steem.reward_pool_balances()
return [self.reward_balance, self.recent_claims, self.base]
```


### rshares_to\_steem

Converts the rshares value returned by **current_vote_value** into a value in steem.


```
v = steem.rshares_to_steem(rshares)
returns float to 4 decimals
```


### check_balances

Uses either the account given as an argument or **steem.mainaccount** to get the currenct balances for SBD, STEEM, Steem Power, Vote Power, and the last time the account voted.


```
bal = steem.check_balances(account=None)
returns a list [float(sbdbal), float(steembal), float(steempower), float(votepower), datetime(lastvotetime)]
```


### current_vote\_value

Using the **lastvotetime**, **steempower**, **voteweight**, and **votepower** values returned from **check_balances** returns the current vote value in rshares. If **votepower** is entered as a value between 1 and 100 the vote value returned will be determined solely by that value. However, if it's in a range from 150 to 10000, which can be entered instead, the vote value returned will be caluculated including the regenerated votepower using **lastvotetime**. **steempower** must be a number between 150 and 10000. **voteweight** must be a number between 1 and 100.

All of these values are return by **check_balances** and can be used like this:


```
(sbd, steem, steempower, votepower, lastvotetime) = steem.check_balances(account)
r = steem.current_vote_value(lastvotetime, steempower, voteweight=100, votepower)
returns a integer value in rshares
```


### transfer_funds

Sends the the amount in the denomination (must be "SBD" or "STEEM" in all caps) and a memo message to another account using **steem.mainaccount** and the keys provided to **steem.keys** (Must provide Steemit Owner Key to transfer funds).

``` 
steem.transfer_funds(to, amount, denom, msg)
returns boolean
```

### get_my\_history

Fetches the history of the account provided, or **steem.mainaccount** and returns it as raw tuple as delivered by steem-python, starting from the most recent activity and to the limit provided, which defaults to 100 actions.

```
h = steem.get_my_history(account=None, limit=100)
returns dict
```

### post

Creates a post to **steem.mainaccount** using **steem.keys** (Private Posting Key must be provided) given a title, the body of the post, an optional permlink and the 5 tags which must be given as a list. ```[tag1, tag2, tag3, tag4, tag5]``` If no permlink is given Steem-Python will create the permlink from the title. Because this action can sometimes be unreliable with the public nodes this method will wait 20 seconds after creating the post, then check the blockchain using the **recent_post** method to verify the post was indeed created. Returns true or false base on whether the post was found.


```
steem.post(title, body, permlink, tags)
returns boolean
```

### reply


Creates a reply to a post using **steem.mainaccount** and **steem.keys** (Private Posting Key must be provided).


```
steem.reply(permlink, msgbody)
returns boolean
```


### follow

Causes **steem.mainaccount** to follow the account given as an argument


```
steem.follow(account)
returns boolean
```


### unfollow

Causes **steem.mainaccount** to unfollow the account given as an argument


```
steem.unfollow(account)
returns boolean
```


### following


Returns a list of the names of the accounts that are following **steem.mainaccount**. You can also access the raw tuple retruned by Steem-Python using **steem.followed**. ```f = steem.followed() print(f['followed']))```


```
f = steem.following(account=None, limit=100)
returns list of account names as strings
```


### recent_post

Returns the identifier to the most recent post on either the account provided or if none is provided from **steem.mainaccount**. If an integer in days in provided for **daysback** it will return the most recent post from that many days back. You can access the raw dict return by Steem-Python and all post details by accessing **steem.blog**.


```
identifier = recent_post(account=None, daysback=0)
author = steem.blog[0]['comment']['author']
returns a string
```


### dex_ticker

Simply grabs the ticker using the steem_instance method and adds it to a class variable.

```
ticker = steem.dex_ticker()
returns a list of ticker variables
```


### steem_to_sbd

Uses the ticker to get the highest bid and moves the steem at that price if no price is provided. If no amount of Steem is specified it checks the account balance and moves all available steem.

```
steem.steem_to_sbd(self, steem=0, price=0, account=None)
returns boolean
```


### sbd_to_steem

Uses the ticker to get the lowest ask and moves the sbd at that price if nor price is provided. If no amount of SBD is specified it checks the accoutn balance and moves all available SBD.

```
steem.sbd_to_steem(self, sbd=0, price=0, account=None)
returns boolean
```


### vote_witness

Uses the steem_instance method to vote on a witness.

```
steem.vote_witness(self, witness, account=None)
retruns boolean
```


### unvote_witness

Uses the steem_instance method to unvote a witness.

```
steem.unvote_witness(self, witness, account=None)
returns boolean
```


### voted_me_witness

Fetches all those a given account is following and sees if they have voted that account as witness.

```
steem.voted_me_witness(self, account=None, limit=100)
returns a list of account names
```


### muted_me

Fetches all those a given account is following and sees if they have muted that account.

```
steem.muted_me(self, account=None, limit=100)
returns list of account names
```


### delegate

Delegates based on Steem Power rather than by vests.

```
steem.delegate(self, to, steempower)
returns boolean
```


# SteemConnect

The SteemConnect utilities can be accessed in a very intuitive way. Just like the SimpleSteem class uses the **steem_instance** method, so the utilities use the **steem.connect.steemconnect** method in a similar way. To use the SteemConnect methods you must either have entered a client ID, client secret key, callback url, and permissions at the time of installing SimpleSteem (see installation instructions) or have instatiated the SimpleSteem class with the same information. 


### auth_url

To use SteemConnect you must first access the SteemConnect website. After logging in with the given permissions, SteemConnect will redirect the user to the given callback url with ?code="XXXXXX" appended where XXXXX represenst a SteemConnect refresh token.


```
url = steem.connect.auth_url()
```

### get_token

A refresh token can then be used to retrieve an access token, which is then used to authorize actions on the blockchain.


```
accesstoken = steem.connect.get_token(refreshtoken)
```

### vote with SteemConnect

Now, with an access token, we can vote on a post given the account to vote on and the permlink and the voteweight using **steem.mainaccount**. The voter argument must be the name of the account that has provided the access token.


```
steem.connect.vote(voter, author, permlink, voteweight)
```

# SimpleSteem Utilities

These utility methods are used by the SimpleClass class and can be accessed directly.

### goodnode

The goodnode method was developed out of a [need to properly handle public steemd websocket server errors](https://steemit.com/utopian-io/@learnelectronics/steem-python-1-0-1-does-not-properly-handle-steemd-websocket-server-errors). If a node in the node list returns a server error from urllib module the next node in the list is tried instead. This method is used by **steem_instance** and should not need to be used directly.

```
steem.util.goodnode([nodelist])
returns first node that does not produce a server error
```

### identifier

Converts a permlink and an author's name into a properly formatted identifier.

```
steem.util.identifier(author, permlink):
returns string
```


### permlink

Separates out the author's name and permlink from an identifier

```
(author, permlink) = steem.util.permlink(identifier)
```


### days_back

Returns an the number of days since a given date.

```
days = steem.util.days_back(datetimeobj)
returns integer
```


### scale_vote

Steem-Python requires certain values be given in the range of 150 to 10000. This method converts 1 to 100 to that range.


```
newvalue = steem.util.scale_vote(value)
returns integer
```


### calc_regenerated

Returns the additional steempower regenerated since a given date.


```
additionalsteempower = steem.util.calc_regenerated(datetimeobj)
returns float
```
















