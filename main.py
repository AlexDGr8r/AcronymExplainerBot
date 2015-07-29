#!/usr/bin/env python

import time
import json
import praw
import OAuth2Util
from collections import deque

USER_AGENT = "PRAW:Acronym Explainer:v0.1 by /u/AlexDGr8r"

r = praw.Reddit(user_agent=USER_AGENT)
o = OAuth2Util.OAuth2Util(r)
cache = deque(maxlen=200)
search_words = ["unbgbbiivchidctiicbg"]

# Load JSON data from config.json
with open('config.json') as data_file:
    config = json.load(data_file)

# Compile subreddits we want to pull the comments from
subreddits = ''
for sub in config['subreddits']:
    subreddits += sub + '+'
subreddits = subreddits[:-1]

while True:
    o.refresh()
    print 'Checking subreddits...'
    multireddits = r.get_subreddit(subreddits)
    comments = multireddits.get_comments()
    for comment in comments:
        if comment.id in cache:
            break
        cache.append(comment.id)

    print 'Going to sleep'
    time.sleep(10)
