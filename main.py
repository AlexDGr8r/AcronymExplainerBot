#!/usr/bin/env python

import time
import json
import praw
import OAuth2Util
from collections import deque
from pprint import pprint

USER_AGENT = "PRAW:Acronym Explainer:v0.1 by /u/AlexDGr8r"
CACHE_FILE_NAME = 'cache.dat'

r = praw.Reddit(user_agent=USER_AGENT)
o = OAuth2Util.OAuth2Util(r)
cache = deque(maxlen=200)

def load_cache(filename):
    try:
        with open(filename) as f:
            cache = deque(f.read().splitlines(), maxlen=200)
    except IOError:
        cache = deque(maxlen=200)
        print('%s does not exist. Ignoring.' % filename)

def save_cache(filename):
    f = open(filename, 'w')
    for item in cache:
        f.write('%s\n' % item)
    f.close()

# TODO rework for database
def reply_to_comment(comment, acronym):
    text = "For those that do not understand what %s stands for, I'm here to help!\n\n### Explanation:\n\n" % acronym
    text += acronyms[acronym] + "\n\n*****\n\n"
    text += "*I am simply a bot. If the information I've displayed is incorrect, please message my creator /u/AlexDGr8r*"
    comment.reply(text)
    print('Replied to a comment')

# Load JSON data from config.json
with open('config.json') as data_file:
    config = json.load(data_file)

# Load the cache
load_cache(CACHE_FILE_NAME)

# Compile subreddits we want to pull the comments from
subreddits = ''
for sub in config['subreddits']:
    subreddits += sub + '+'
subreddits = subreddits[:-1]

try:
    while True:
        o.refresh()
        print 'refreshed and ready to go!'
        multireddits = r.get_subreddit(subreddits)
        comments = multireddits.get_comments()
        for comment in comments:
            if comment.id in cache:
                print('Breaking...')
                break
            if comment.author.name == "AcronymExplainerBot":
                print('ignoring my own comment')
                continue
            cache.append(comment.id)
            print('appended to cache')
            # TODO USE sqlite db instead of json

        print 'Going to sleep'
        time.sleep(2)
except (KeyboardInterrupt, SystemExit):
    save_cache(CACHE_FILE_NAME)
    print('Saved cache')
    print('exiting')
