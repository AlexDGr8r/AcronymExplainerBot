#!/usr/bin/env python

import time
# import json
import praw
from praw.errors import InvalidUser, InvalidUserPass, RateLimitExceeded, HTTPException, OAuthAppRequired
from praw.objects import Comment, Submission

user_agent = "PRAW:UNBGBBIIVCHIDCTIICBG Monitor:v0.1 by /u/AlexDGr8r"
r = praw.Reddit(user_agent=user_agent)
try:
    r.refresh_access_information();
    print 'Logged in with OAuth'
except (HTTPException, OAuthAppRequired) as e:
    try:
        r.login()
    except InvalidUser as e:
        raise InvalidUser("User does not exist.", e)
    except InvalidUserPass as e:
        raise InvalidUserPass("Specified an incorrect password.", e)
    except RateLimitExceeded as e:
        raise RateLimitExceeded("You're doing that too much.", e)

already_done = []
search_words = ["unbgbbiivchidctiicbg"]

while True:
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
