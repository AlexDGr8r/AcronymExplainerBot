#!/usr/bin/env python

import time
import praw

user_agent = "PRAW:UNBGBBIIVCHIDCTIICBG Monitor:v0.1 by /u/AlexDGr8r"
r = praw.Reddit(user_agent=user_agent)
r.login()

already_done = []
search_words = ["unbgbbiivchidctiicbg"]

while True:
    subreddit = r.get_subreddit('alexthegreater')
    for submission in subreddit.get_new(limit=10):
        if submission.is_self:
            self_text = submission.selftext.lower()
            has_referenced = any(string in self_text for string in search_words)
            if submission.id not in already_done and has_referenced:
                msg = '[Link to reference!](%s)' % submission.short_link
                r.send_message('AlexDGr8r', 'Found a reference!', msg)
                already_done.append(submission.id)
    time.sleep(15)
