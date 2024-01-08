# Insta-Auto-DM

instagram bot for auto dm after publishing comment on a post !

## Set parameters

Inside of **src/**

-   '**account.json**' file: set an valid instagram account
-   '**keywords**' file: words you want to see in a comment before handling dm
-   '**message**' file : set the massage you want to send
-   '**post**' file: id of the instagram post you want to tracked (get it in the post url)

## Install package

```python
pip install -r rqs.txt

pip3 install -r rqs.txt # for macOS & Linux
```

## Run the bot

```python
cd src/ # move to the src/ folder
py bot.py # run with python

python3 bot.py # for macOS & Linux
```

## Features

[x] detect new comments  
[x] detect if comment contains specified keywords  
[x] auto dm user who published comment
