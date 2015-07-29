#!/usr/bin/env python

import time
# import json
import praw
import OAuth2Util

user_agent = "PRAW:Acronym Explainer:v0.1 by /u/AlexDGr8r"
r = praw.Reddit(user_agent=user_agent)
o = OAuth2Util.OAuth2Util(r)

already_done = []
search_words = ["unbgbbiivchidctiicbg"]

while True:
    o.refresh()
    print 'Checking subreddit...'
    subreddit = r.get_subreddit('alexthegreater')
    for submission in subreddit.get_new(limit=10):
        if submission.is_self:
            print 'Self submission found'
            self_text = submission.selftext.lower()
            has_referenced = any(string in self_text for string in search_words)
            if submission.id not in already_done and has_referenced:
                print 'Have not checked this post yet'
                print 'sending message'
                msg = '[Link to reference!](%s)' % submission.short_link
                r.send_message('AlexDGr8r', 'Found a reference!', msg)
                already_done.append(submission.id)
    print 'Going to sleep'
    time.sleep(10)
