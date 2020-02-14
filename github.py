#!/usr/bin/env python3

import sys
import os
import json
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.utils import parseaddr
from subprocess import Popen, PIPE



def github_ping(pl):
    t = "Event: ping\n\n"
    t += "Type: " + str(pl['hook']['type']) + "\n"
    if (pl['hook']['type'] == "Organization"):
        t += "Organization: " + str(pl['organization']['login']) + "\n"
        s = "[" + str(pl['organization']['login']) + "]: ping"
    elif (pl['hook']['type'] == "Repository"):
        t += "Repository Name: " + str(pl['repository']['name']) + "\n"
        t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
        t += "Description: " + str(pl['repository']['description']) + "\n"
        t += "URL: " + str(pl['repository']['html_url']) + "\n"
        t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"
        if ('organization' in pl):
            s = "[" + str(pl['organization']['login']) + "]: ping"
        else:
            s = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]: ping"
    else:
        t += "Unknown ping, dumping data\n\n"
        t += json.dumps(pl, indent=2, sort_keys=True)
        t += "\n\n"
    t += "Sender: " + str(pl['sender']['login'])

    return s, t


def github_push(pl):
    t = "Event: push\n\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"
    t += "Pushed by: " + str(pl['pusher']['name']) + "\n\n\n"
    t += "Commits:\n\n"
    for c in pl['commits']:
        t += "Author: " + str(c['author']['name']) + "\n"
        t += "Committer: " + str(c['committer']['name']) + "\n"
        t += "Timestamp: " + str(c['timestamp']) + "\n"
        t += "ID: " + str(c['id']) + "\n"
        t += "Commit URL: " + str(c['url']) + "\n\n"
        t += "Message:\n" + str(c['message']) + "\n\n\n"
        t += "Modified:\n" + str("\n".join(c['modified'])) + "\n\n\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    # if a tag is created, no commit messages is included
    if (pl['commits']):
        cm = (pl['commits'][0]['message']).split('\n', 1)[0]
        s = s_cm + " " + str(cm)
    else:
        s = s_cm + " tag/branch"

    return s, t


def github_repository(pl):
    t = "Event: repository\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Repository " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_watch(pl):
    t = "Event: Watch\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Repository " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_star(pl):
    t = "Event: Star\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Repository " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_issues(pl):
    t = "Event: Issues\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['issue']['title'])):
        t += "Title: " + str(pl['issue']['title']) + "\n"
    if (str(pl['action']) == "labeled"):
        if (str(pl['issue']['labels'][0]['name'])):
            for l in pl['issue']['labels']:
                t += "Label: " + str(l['name']) + "\n"
    if (str(pl['issue']['body'])):
        t += "Description:\n" + str(pl['issue']['body']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Issue " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_else(eventtype, pl):
    t = "Event: " + str(eventtype) + "\n\n"
    t += json.dumps(pl, indent=2, sort_keys=True)

    s = "Unknown GitHub event: " + str(eventtype)

    return s, t




#######################################################################
# main


# command line arguments
email_from = sys.argv[1]
email_to = sys.argv[2]
eventtype = sys.argv[3]
payload = sys.argv[4]
pl = json.loads(payload)
pl = json.loads(pl['payload'])


# verify email addresses
email_verify_from = parseaddr(email_from)
if (email_verify_from[1] == ''):
    print("Failed to verify 'From' address!")
    sys.exit(1)
email_from = email_verify_from[1]

email_verify_to = parseaddr(email_to)
if (email_verify_to[1] == ''):
    print("Failed to verify 'To' address!")
    sys.exit(1)
email_to = email_verify_to[1]



# parse GitHub events
# generate email message
if (eventtype == "ping"):
    subject, message = github_ping(pl)
elif (eventtype == "push"):
    subject, message = github_push(pl)
elif (eventtype == "repository"):
    subject, message = github_repository(pl)
elif (eventtype == "watch"):
    subject, message = github_watch(pl)
elif (eventtype == "star"):
    subject, message = github_star(pl)
elif (eventtype == "issues"):
    subject, message = github_issues(pl)
else:
    subject, message = github_else(eventtype, pl)


# generare email, and send it
msg = MIMEText(message)
msg["From"] = email_from
msg["To"] = email_to
msg["Subject"] = subject
msg.add_header("X-Notification-Type", "GitHub")
p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
p.communicate(msg.as_string())




sys.exit(0)
