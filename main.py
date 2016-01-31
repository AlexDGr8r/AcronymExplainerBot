#!/usr/bin/env python

import time
import json
import re
import praw
import OAuth2Util
import acrodb
from collections import deque

USER_AGENT = "PRAW:Acronym Explainer:v0.1 by /u/AlexDGr8r"
CACHE_FILE_NAME = 'cache.dat'

r = praw.Reddit(user_agent=USER_AGENT)
o = OAuth2Util.OAuth2Util(r)

def load_cache(filename):
    try:
        f = open(filename, 'r')
        lines = f.read().splitlines();
        return deque(lines, maxlen=200)
    except IOError:
        print('%s does not exist. Ignoring.' % filename)
        return deque(maxlen=200)

def save_cache(filename):
    f = open(filename, 'w')
    for item in cache:
        f.write('%s\n' % item)
    f.close()

def reply_to_comment(comment, acronym, acronyms):
    text = "For those that do not understand what **%s** stands for, I'm here to help!\n\n### Explanation(s):\n\n***\n\n" % acronym
    for acro_dict in acronyms:
        text += "> %s\n\n***\n\n" % acro_dict['Description']
    text += "*I am simply a bot. If the information I've displayed is incorrect, please message my creator /u/AlexDGr8r.*"
    comment.reply(text)
    print('Replied to a comment')

###################### Begin Script ######################

# Load JSON data from config.json
with open('config.json') as data_file:
    config = json.load(data_file)

# Load the cache
cache = load_cache(CACHE_FILE_NAME)

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

            cache.append(comment.id)
            print('appended to cache')

            if comment.author.name == "AcronymExplainerBot":
                print('ignoring my own comment')
                continue

            match = re.match(r'!acro(nym)?s?bot (\w+)', comment.body.lstrip(), re.I)
            if match:
                acro = match.group(2).upper() # the acronym is subgroup 2
                local_results = acrodb.getAcronym(acro)
                if len(local_results) > 0:
                    reply_to_comment(comment, acro, local_results)
                else:
                    print("Not in local database. Ignoring for now")
                    # TODO check abbreviations.com API if not in local database

        print 'Going to sleep'
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    save_cache(CACHE_FILE_NAME)
    print('Saved cache')
    acrodb.close()
    print('exiting')
