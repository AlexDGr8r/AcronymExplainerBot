#!/usr/bin/env python

import time
import json
import re
import praw
import OAuth2Util
import urllib2
import xmltodict
import acrodb
from collections import deque

USER_AGENT = "PRAW:Acronym Explainer:v0.1 by /u/AlexDGr8r"
CACHE_FILE_NAME = 'cache.dat'

r = praw.Reddit(user_agent=USER_AGENT)
o = OAuth2Util.OAuth2Util(r)
comment_queue = []

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
    num_described = 0
    views, more = acrodb.getPopularity(acronym)
    text = "For those that do not understand what **%s** stands for, I'm here to help!\n\nDescription for %s |\n-------- |\n" % (acronym, acronym)
    for description in acronyms:
        if num_described == 10:
            break
        text += "%s |\n" % description
        num_described += 1
    if more == True:
        text += "**There are even more explanations on [abbreviations.com](http://www.abbreviations.com/). Check them out [here!](http://www.abbreviations.com/%s)**\n" % acronym.upper()
    if views > 1:
        text += "\n**This acronym has been requested %d times.**\n" % views
    else:
        text += "\n**This is the first time this acronym has been requested.**\n"
    text += "***\n^(I am simply a bot. If the information I've displayed is incorrect, please message my creator /u/AlexDGr8r.)"
    try:
        comment.reply(text)
        print('Replied to a comment')
    except praw.errors.RateLimitExceeded as error:
        comm_dict = {"comment":comment, "text":text, "time":time.time() + error.sleep_time}
        comment_queue.append(comm_dict)
        print('Comment added to queue due to exceeding rate limit')

def getDescriptionsFromAPI(acronym, uid, token):
    xmlfile = urllib2.urlopen('http://www.stands4.com/services/v2/abbr.php?uid=%s&tokenid=%s&term=%s' % (uid, token, acronym.upper()))
    data = xmlfile.read()
    xmlfile.close()
    jsondata = xmltodict.parse(data)
    results = jsondata['results']
    descriptions = []
    if results is not None:
        terms = results['result']
        for term in terms:
            desc = term['definition']
            if desc in descriptions:
                # ignore duplicate definitions
                continue
            descriptions.append(desc)
    return descriptions

###################### Begin Script ######################

# Load JSON data from config.json
with open('config.json') as data_file:
    config = json.load(data_file)

# Load the cache
cache = load_cache(CACHE_FILE_NAME)

# Abbreviations.com API credentials
API_UID = config['API_UID']
API_TOKEN = config['API_Token']

# Compile subreddits we want to pull the comments from
subreddits = ''
for sub in config['subreddits']:
    subreddits += sub + '+'
subreddits = subreddits[:-1]

try:
    while True:
        o.refresh()

        # Check backlog
        curr_time = time.time()
        for comment_dict in comment_queue:
            if curr_time >= comment_dict["time"]:
                try:
                    comment_dict["comment"].reply(comment_dict["text"])
                    print("backlogged comment replied to")
                    comment_queue.remove(comment_dict)
                except praw.errors.RateLimitExceeded as error:
                    comment_dict["time"] = curr_time + error.sleep_time
                    print("backlogged comment still exceeding rate limit")

        # Check new comments
        print 'Checking for new comments...'
        multireddits = r.get_subreddit(subreddits)
        comments = multireddits.get_comments()
        for comment in comments:
            if comment.id in cache:
                print('No new comments')
                break

            cache.append(comment.id)
            print('found new comment')

            if comment.author.name == "AcronymExplainerBot":
                print('ignoring my own comment')
                continue

            match = re.match(r'!acro(nym)?s?bot (\w+)', comment.body.lstrip(), re.I)
            if match:
                acro = match.group(2).upper()   # the acronym is subgroup 2
                print "acronym requested: %s" % acro
                local_results = acrodb.getAcronym(acro)
                if len(local_results) > 0:      # Found in local database, no need to use API
                    acrodb.increasePopularity(acro)
                    reply_to_comment(comment, acro, local_results)
                else:
                    descriptions = getDescriptionsFromAPI(acro, API_UID, API_TOKEN)
                    if len(descriptions) > 0:
                        more = False
                        if len(descriptions) > 10:
                            more = True
                        acrodb.addAcronyms(acro, descriptions, more)
                        reply_to_comment(comment, acro, descriptions)
                    else:
                        print "Could not find anything for %s" % acro

        print 'Resting'
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    save_cache(CACHE_FILE_NAME)
    print('Saved cache')
    acrodb.close()
    print('exiting')
