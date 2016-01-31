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
    except praw.errors.RateLimitExceeded as error:
        print("Sleeping for %d seconds due to exceeding rate limit" % error.sleep_time)
        time.sleep(error.sleep_time)
        comment.reply(text)
    print('Replied to a comment')

def getDescriptionsFromAPI(acronym, uid, token):
    xmlfile = urllib2.urlopen('http://www.stands4.com/services/v2/abbr.php?uid=%s&tokenid=%s&term=%s' % (uid, token, acronym.upper()))
    data = xmlfile.read()
    xmlfile.close()
    jsondata = xmltodict.parse(data)
    results = jsondata['results']
    terms = results['result']
    descriptions = []
    for term in terms:
        desc = term['definition']
        if desc in descriptions:
            print('Duplicate defintion, ignoring')
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
print('UID=%s' % API_UID)
API_TOKEN = config['API_Token']
print('token=%s' % API_TOKEN)

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
                acro = match.group(2).upper()   # the acronym is subgroup 2
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

        print 'Going to sleep'
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    save_cache(CACHE_FILE_NAME)
    print('Saved cache')
    acrodb.close()
    print('exiting')
