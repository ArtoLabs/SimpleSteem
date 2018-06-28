# Installing SimpleSteem

The best way to install SimpleSteem and to ensure you have all dependencies use pip3.

### Either

```
pip3 install simplesteem --user pip
```

### Or

```
sudo -H pip3 install simplesteem
```

# Setup

After installing SimpleSteem, the first time you instatiate the SimpleSteem class **makeconfig.py** is envoked as a one-time runjob to create **config.py**. This sets up the configuration parameters which are requested one at a time by command prompt. The parameters requested are:

### mainaccount

Enter the name of the default account to be used by SimpleSteem method calls when no other account is specified. If no value is entered the default account will be "ned".

### keys

Enter the private posting and owner keys in the exact same format as they would be given while instatiating the SimpleSteem class.

```
['XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX']
```

### nodes

Enter the nodes in the exact same format as they would be given while instatiating the SimpleSteem class. If no value is entered this defaults to the following node list.

```
["https://steemd.minnowsupportproject.org",
    "https://steemd.privex.io",
    "https://gtg.steem.house:8090",
    "https://steemd.pevo.science",
    "https://rpc.steemliberator.com"]
```

### client_id

This is the client ID provided when creating a SteemConnect app.

### client_secret

This is the client secret provided when creating a SteemConnect app.

### callback_url

The callback url used by SteemConnect when creating a refresh token.

### permissions

The permissions granted to you SteemConnect app when a user authenticates. Defaults to the minimum values:

```
login,offline,vote
```

### logpath

The path to where ScreenLogger creates and writes error messages. To make sure the file permissions are set correctly it's best if SimpleSteem is first instatiated using sudo or administrator privileges. If this value is left blank it defaults to the folder to which SimpleSteem has been installed. 

### screenmode

If set to ```quiet``` ScreenLogger writes only to the log file and not to screen.


