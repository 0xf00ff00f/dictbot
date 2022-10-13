A simple dictionary bot for our Japanese study group Discord server.

## Running

Grab the [EDICT](http://www.edrdg.org/jmdict/edict.html) dictionary file and convert it to UTF-8:

```
wget http://ftp.edrdg.org/pub/Nihongo/edict.gz
gunzip -c edict.gz | iconv - -f EUC-JP -t UTF-8 > edict.utf
```

Set the DISCORD_TOKEN environment variable and run the script.
