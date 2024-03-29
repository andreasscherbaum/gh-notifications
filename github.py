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


def github_pull_request_review(pl):
    t = "Event: Pull Request Review\n\n"
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

    t += "\n"
    if (str(pl['review']['html_url'])):
        t += "Review URL: " + str(pl['review']['html_url']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Pull Request Review " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_pull_request_review_thread(pl):
    t = "Event: Pull Request Review Thread\n\n"
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

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Pull Request Review Thread " + str(pl['action']) + ": " + str(pl['repository']['name'])

    return s, t


def github_pull_request_review_comment(pl):
    t = "Event: Pull Request Review Comment\n\n"
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

    t += "\n"
    if (str(pl['comment']['html_url'])):
        t += "Comment URL: " + str(pl['comment']['html_url']) + "\n"
    if (str(pl['comment']['body'])):
        t += "Comment:\n" + str(pl['comment']['body']) + "\n"

    if ('organization' in pl):
        s_cm = "[" + str(pl['organization']['login']) + "/" + str(pl['repository']['name']) + "]"
    else:
        s_cm = "[" + str(pl['repository']['owner']['login']) + "/" + str(pl['repository']['name']) + "]"

    s = "Pull Request Review Comment " + str(pl['action']) + ": " + str(pl['repository']['name'])

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


def github_check_run(pl):
    t = "Event: check_run " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('status' in pl['check_run']):
        t += "Status: " + str(pl['check_run']['status']) + "\n"
    if ('conclusion' in pl['check_run']):
        t += "Conclusion: " + str(pl['check_run']['conclusion']) + "\n"
    if ('details_url' in pl['check_run']):
        t += "Details: " + str(pl['check_run']['details_url']) + "\n"

    s = "Check_run: " + str(pl['action'])

    return s, t


def github_check_suite(pl):
    t = "Event: check_suite " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('status' in pl['check_suite']):
        t += "Status: " + str(pl['check_suite']['status']) + "\n"
    if ('conclusion' in pl['check_suite']):
        t += "Conclusion: " + str(pl['check_suite']['conclusion']) + "\n"
    if ('url' in pl['check_suite']):
        t += "Details: " + str(pl['check_suite']['url']) + "\n"
    if ('message' in pl['check_suite']['head_commit']):
        t += "\nCommit message: " + str(pl['check_suite']['head_commit']['message']) + "\n"

    s = "Check_suite: " + str(pl['action'])

    return s, t


def github_workflow_job(pl):
    t = "Event: workflow_job " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('status' in pl['workflow_job']):
        t += "Status: " + str(pl['workflow_job']['status']) + "\n"
    if ('name' in pl['workflow_job']):
        t += "Name: " + str(pl['workflow_job']['name']) + "\n"
    if ('html_url' in pl['workflow_job']):
        t += "Details: " + str(pl['workflow_job']['html_url']) + "\n"

    s = "Workflow_job: " + str(pl['action'])

    return s, t


def github_workflow_run(pl):
    t = "Event: workflow_run " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    t += "\n"
    if ('name' in pl['workflow']):
        t += "Workflow Name: " + str(pl['workflow']['name']) + "\n"
    if ('path' in pl['workflow']):
        t += "Workflow Path: " + str(pl['workflow']['path']) + "\n"
    if ('state' in pl['workflow']):
        t += "Workflow Status: " + str(pl['workflow']['state']) + "\n"
    t += "\n"

    if ('name' in pl['workflow_run']):
        t += "Workflow Run Name: " + str(pl['workflow_run']['name']) + "\n"
    if ('html_url' in pl['workflow_run']):
        t += "Workflow Run Details: " + str(pl['workflow_run']['html_url']) + "\n"
    if ('status' in pl['workflow_run']):
        t += "Workflow Run Status: " + str(pl['workflow_run']['status']) + "\n"

    s = "Workflow_run: " + str(pl['action'])

    return s, t


def github_deploy_key(pl):
    t = "Event: deploy_key " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('title' in pl['key']):
        t += "Key title: " + str(pl['key']['title']) + "\n"
    if ('url' in pl['key']):
        t += "Key url: " + str(pl['key']['url']) + "\n"
    if ('read_only' in pl['key']):
        t += "Key read-only: " + str(pl['key']['read_only']) + "\n"
    if ('verified' in pl['key']):
        t += "Key verified: " + str(pl['key']['verified']) + "\n"

    s = "Deploy_key: " + str(pl['action'])

    return s, t


def github_branch_protection_rule(pl):
    t = "Event: branch_protection_rule " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('name' in pl['rule']):
        t += "Rule name: " + str(pl['rule']['name']) + "\n"
    keys = ['admin_enforced',
            'allow_deletions_enforcement_level',
            'allow_force_pushes_enforcement_level',
            'authorized_actors_only',
            'authorized_dismissal_actors_only',
            'create_protected',
            'dismiss_stale_reviews_on_push',
            'ignore_approvals_from_contributors',
            'linear_history_requirement_enforcement_level',
            'merge_queue_enforcement_level',
            'pull_request_reviews_enforcement_level',
            'require_code_owner_review',
            'require_last_push_approval',
            'required_approving_review_count',
            'required_conversation_resolution_level',
            'required_deployments_enforcement_level',
            'required_status_checks_enforcement_level',
            'signature_requirement_enforcement_level',
            'strict_required_status_checks_policy']
            
    for key in keys:
      if (key in pl['rule']):
          t += "Rule " + key + ": " + str(pl['rule'][key]) + "\n"

    s = "Branch Protection Rule: " + str(pl['action'])

    return s, t


def github_dependabot_alert(pl):
    t = "Event: dependabot_alert " + str(pl['action']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('dependency' in pl['alert']):
        t += "Dependency Manifest Path: " + str(pl['alert']['dependency']['manifest_path']) + "\n"
        t += "Dependency Package Name: " + str(pl['alert']['dependency']['package']['name']) + "\n"
        t += "Dependency Package Ecosystem: " + str(pl['alert']['dependency']['package']['ecosystem']) + "\n"
    if ('security_advisory' in pl['alert']):
        t += "Description: " + str(pl['alert']['security_advisory']['description']) + "\n"
    if ('state' in pl['alert']):
        t += "State: " + str(pl['alert']['state']) + "\n"

    s = "Branch Protection Rule: " + str(pl['action'])

    s = "Dependabot Alert: " + str(pl['action'])

    return s, t


def github_status(pl):
    t = "Event: status " + str(pl['state']) + "\n"
    t += "\n"
    t += "Sender: " + str(pl['sender']['login']) + "\n"
    t += "Repository Name: " + str(pl['repository']['name']) + "\n"
    t += "Repository Full: " + str(pl['repository']['full_name']) + "\n"
    if (str(pl['repository']['description']) != "null"):
        t += "Description: " + str(pl['repository']['description']) + "\n"
    t += "URL: " + str(pl['repository']['html_url']) + "\n"
    t += "Owner: " + str(pl['repository']['owner']['login']) + "\n\n"

    if ('context' in pl):
        t += "Context: " + str(pl['context']) + "\n"
    if ('description' in pl):
        t += "Description: " + str(pl['description']) + "\n"
    if ('state' in pl):
        t += "State: " + str(pl['state']) + "\n"
    if ('created_at' in pl):
        t += "Created at: " + str(pl['created_at']) + "\n"
    if ('updated_at' in pl):
        t += "Updated at: " + str(pl['updated_at']) + "\n"
    if ('target_url' in pl):
        t += "Target URL: " + str(pl['target_url']) + "\n"

    s = "Status: " + str(pl['state'])

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
elif (eventtype == "pull_request_review"):
    subject, message = github_pull_request_review(pl)
elif (eventtype == "pull_request_review_thread"):
    subject, message = github_pull_request_review_thread(pl)
elif (eventtype == "pull_request_review_comment"):
    subject, message = github_pull_request_review_comment(pl)
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
elif (eventtype == "check_run"):
    subject, message = github_check_run(pl)
elif (eventtype == "check_suite"):
    subject, message = github_check_suite(pl)
elif (eventtype == "check_suite"):
    subject, message = github_check_suite(pl)
elif (eventtype == "workflow_job"):
    subject, message = github_workflow_job(pl)
elif (eventtype == "workflow_run"):
    subject, message = github_workflow_run(pl)
elif (eventtype == "deploy_key"):
    subject, message = github_deploy_key(pl)
elif (eventtype == "branch_protection_rule"):
    subject, message = github_branch_protection_rule(pl)
elif (eventtype == "dependabot_alert"):
    subject, message = github_dependabot_alert(pl)
elif (eventtype == "status"):
    subject, message = github_status(pl)
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
