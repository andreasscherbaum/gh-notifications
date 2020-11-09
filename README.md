# gh-notifications

Notifications for GitHub Webhook events


## About

This script is used to "catch" and process [GitHub Webhook events](https://developer.github.com/webhooks/), and generate an useful email from the payload.


## Dependencies

This script is written in Python.

The following modules are used:

* sys
* os
* json
* smtplib
* email.message
* email.mime.text
* email.utils
* subprocess


## Install Webhook

In the Repository settings, click on "Webhooks". Click "Add webhook."

As "Payload URL" specify the website which uses this script here.

Content type: application/x-www-form-urlencoded

Specify a Secret.

Enable SSL verification (you better have this enabled for your webhook service).

Specify that all events (not just commits) shall trigger the webhook.

Finally, click "Add webhook".


## Using 'webhook' with this script

The [webhook](https://github.com/adnanh/webhook) tool can be used to receive GitHub Webhooks. I blogged about the setup [here](https://andreas.scherbaum.la/blog/archives/987-webhook-service-with-TLS-and-Lets-Encrypt-certificate.html).

The following is an example how to setup _webhook_:

```
[
  {
    "id": "github",
    "execute-command": "/path/to/github.py",
    "command-working-directory": "/tmp",
    "pass-arguments-to-command":
    [
        {
          "source": "string",
          "name": "no-reply@your.domain"
        },
        {
          "source": "string",
          "name": "address@your.domain"
        },
        {
          "source": "header",
          "name": "X-Github-Event"
        },
        {
          "source": "entire-payload"
        }
    ],
    "response-message": "OK",
    "trigger-rule":
    {
        "match":
        {
            "type": "payload-hash-sha1",
            "secret": "secret",
            "parameter":
            {
                "source": "header",
                "name": "X-Hub-Signature"
            }
        }
    }
  }
]
```

A few things need to be replaced:
* "no-reply@your.domain": that is the email address used as "From" in any email
* "address@your.domain": that is the email receiver
* "/path/to/github.py": the path to the _github.py_ script
* "id": that is the URL path for _webhook_
* "secret": the secret entered into the GitHub webhook page


## Recognized GitHub events

Currently this script recognizes the following GitHub events:
* ping
* push
* repository
* watch
* star
* issues
* member
* commit_comment
* issue_comment
* fork
* pull_request
* meta
* create
* delete (branch)
* repository_vulnerability_alert
* project
* label
* check_run
* check_suite
* deploy_key

It will generate an email with unknown events.


## pre-commit hook

The included file _pre-commit_ can be placed in _.git/hooks_ and will ensure that the _README.md_ is updated if changes are applied to the Python script.
