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

    s = "Repository Watch " + str(pl['action']) + ": " + str(pl['repository']['name'])

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

    if (pl['action'] == 'created'):
        s = "Repository Star starred: " + str(pl['repository']['name'])
    else:
        s = "Repository Star " + str(pl['action']) + ": " + str(pl['repository']['name'])

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


def github_member(pl):
    t = "Event: Member\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['member']['login'])):
        t += "Account: " + str(pl['member']['login']) + "\n"
    if (str(pl['member']['type'])):
        t += "Type: " + str(pl['member']['type']) + "\n"
    if (str(pl['member']['site_admin'])):
        t += "Site Admin: " + str(pl['member']['site_admin']) + "\n"
    if (str(pl['member']['url'])):
        t += "URL: " + str(pl['member']['url']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Member " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_commit_comment(pl):
    t = "Event: Commit Comment\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['comment']['user']['login'])):
        t += "Account: " + str(pl['comment']['user']['login']) + "\n"
    if (str(pl['comment']['user']['type'])):
        t += "Type: " + str(pl['comment']['user']['type']) + "\n"
    if (str(pl['comment']['user']['url'])):
        t += "URL: " + str(pl['comment']['user']['url']) + "\n"
    t += "\n\n"
    if (str(pl['comment']['created_at'])):
        t += "Created At: " + str(pl['comment']['created_at']) + "\n"
    if (str(pl['comment']['commit_id'])):
        t += "Commit ID: " + str(pl['comment']['commit_id']) + "\n"
    if (str(pl['comment']['author_association'])):
        t += "Author Association: " + str(pl['comment']['author_association']) + "\n"
    if (str(pl['comment']['html_url'])):
        t += "Comment URL: " + str(pl['comment']['html_url']) + "\n"
    t += "\n"
    if (str(pl['comment']['body'])):
        t += "Comment: " + str(pl['comment']['body']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Commit Comment " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_issue_comment(pl):
    t = "Event: Issue Comment\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['comment']['user']['login'])):
        t += "Account: " + str(pl['comment']['user']['login']) + "\n"
    if (str(pl['comment']['user']['type'])):
        t += "Type: " + str(pl['comment']['user']['type']) + "\n"
    if (str(pl['comment']['user']['url'])):
        t += "URL: " + str(pl['comment']['user']['url']) + "\n"
    t += "\n\n"
    if (str(pl['comment']['created_at'])):
        t += "Created At: " + str(pl['comment']['created_at']) + "\n"
    if (str(pl['comment']['author_association'])):
        t += "Author Association: " + str(pl['comment']['author_association']) + "\n"
    if (str(pl['comment']['html_url'])):
        t += "Comment URL: " + str(pl['comment']['html_url']) + "\n"
    t += "\n"
    if (str(pl['comment']['body'])):
        t += "Comment: " + str(pl['comment']['body']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Issue Comment " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_fork(pl):
    t = "Event: Fork\n\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    t += "Forked to:\n"
    t += "Repository Name: " + str(pl['forkee']['name']) + "\n"
    t += "Repository Full: " + str(pl['forkee']['full_name']) + "\n"
    t += "URL: " + str(pl['forkee']['html_url']) + "\n"
    t += "Owner: " + str(pl['forkee']['owner']['login']) + "\n"
    t += "Private: " + str(pl['forkee']['private']) + "\n"
    t += "Public: " + str(pl['forkee']['public']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Fork: " + str(pl['repository']['name'])

    return s, t


def github_pull_request(pl):
    t = "Event: Pull Request (on your repository)\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['pull_request']['title'])):
        t += "Title: " + str(pl['pull_request']['title']) + "\n"
    t += "\n"
    if (str(pl['pull_request']['user']['login'])):
        t += "User: " + str(pl['pull_request']['user']['login']) + "\n"
    if (str(pl['pull_request']['_links']['html']['href'])):
        t += "URL: " + str(pl['pull_request']['_links']['html']['href']) + "\n"
    if (str(pl['pull_request']['additions'])):
        t += "Additions: " + str(pl['pull_request']['additions']) + "\n"
    if (str(pl['pull_request']['deletions'])):
        t += "Deletions: " + str(pl['pull_request']['deletions']) + "\n"
    if (str(pl['pull_request']['changed_files'])):
        t += "Changed Files: " + str(pl['pull_request']['changed_files']) + "\n"
    if (str(pl['pull_request']['commits'])):
        t += "Commits: " + str(pl['pull_request']['commits']) + "\n"
    if (str(pl['pull_request']['comments'])):
        t += "Comments: " + str(pl['pull_request']['comments']) + "\n"
    if (str(pl['pull_request']['draft'])):
        t += "Draft: " + str(pl['pull_request']['draft']) + "\n"
    if (str(pl['pull_request']['state'])):
        t += "State: " + str(pl['pull_request']['state']) + "\n"

    t += "\n"
    if (str(pl['pull_request']['body'])):
        t += "Comment: " + str(pl['pull_request']['body']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Pull Request " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_meta(pl):
    t = "Event: Meta\n\n"
    t += "Action: " + str(pl['action']) + "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"

    t += "\n\n"
    if (str(pl['hook']['config']['url'])):
        t += "Hook: " + str(pl['hook']['config']['url']) + "\n"
    t += "\n"

    s = "Meta " + str(pl['action'])

    return s, t


def github_create(pl):
    t = "Event: Create Pull Request (on another repository)\n\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['master_branch'])):
        t += "Master Branch: " + str(pl['master_branch']) + "\n"
    if (str(pl['ref'])):
        t += "Ref: " + str(pl['ref']) + "\n"
    if (str(pl['ref_type'])):
        t += "Ref Type: " + str(pl['ref_type']) + "\n"

    s = "Pull Request created from: " + str(pl['repository']['name'])

    return s, t


def github_delete_branch(pl):
    t = "Event: Delete branch\n\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['ref'])):
        t += "Ref: " + str(pl['ref']) + "\n"
    if (str(pl['ref_type'])):
        t += "Ref Type: " + str(pl['ref_type']) + "\n"

    s = "Branch deleted from: " + str(pl['repository']['name'])

    return s, t


def github_repository_vulnerability_alert(pl):
    t = "Event: Repository Vulnerability Alert\n\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['alert']['affected_package_name'])):
        t += "Package: " + str(pl['alert']['affected_package_name']) + "\n"
    if (str(pl['alert']['affected_range'])):
        t += "Affected range: " + str(pl['alert']['affected_range']) + "\n"
    if (str(pl['alert']['external_identifier'])):
        t += "External identifier: " + str(pl['alert']['external_identifier']) + "\n"
    if (str(pl['alert']['external_reference'])):
        t += "External reference: " + str(pl['alert']['external_reference']) + "\n"
    if (str(pl['alert']['fixed_in'])):
        t += "Fixed in: " + str(pl['alert']['fixed_in']) + "\n"

    s = "Repository Vulnerability Alert: " + str(pl['repository']['name'])

    return s, t


def github_project(pl):
    t = "Event: Project " + str(pl['action']) + "\n\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    t += "\n\n"
    if (str(pl['project']['html_url'])):
        t += "URL: " + str(pl['project']['html_url']) + "\n"
    if (str(pl['project']['body'])):
        t += "Body:\n\n" + str(pl['project']['body']) + "\n"

    s = "Project: " + str(pl['action'])

    return s, t


def github_label(pl):
    t = "Event: Label " + str(pl['action']) + "\n"
    if (str(pl['label']['name'])):
        t += "Label: " + str(pl['label']['name']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n"

    s = "Label: " + str(pl['label']['name'])

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
elif (eventtype == "member"):
    subject, message = github_member(pl)
elif (eventtype == "commit_comment"):
    subject, message = github_commit_comment(pl)
elif (eventtype == "issue_comment"):
    subject, message = github_issue_comment(pl)
elif (eventtype == "fork"):
    subject, message = github_fork(pl)
elif (eventtype == "pull_request"):
    subject, message = github_pull_request(pl)
elif (eventtype == "meta"):
    subject, message = github_meta(pl)
elif (eventtype == "create"):
    subject, message = github_create(pl)
elif (eventtype == "delete" and pl['ref_type'] == 'branch'):
    subject, message = github_delete_branch(pl)
elif (eventtype == "repository_vulnerability_alert"):
    subject, message = github_repository_vulnerability_alert(pl)
elif (eventtype == "project"):
    subject, message = github_project(pl)
elif (eventtype == "label"):
    subject, message = github_label(pl)
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
