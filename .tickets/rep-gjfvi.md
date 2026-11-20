---
id: rep-gjfvi
status: closed
deps: []
links: []
created: 2026-11-20T23:28:48Z
type: feature
priority: 2
assignee: Stavros Korokithakis
---
# Send ntfy notification on startup, remove --test-notification

ready for implementation

Objective: the bot sends one ntfy notification when it starts, so the owner can see that the notification channel works. The bot runs unattended in Docker, so the startup message replaces the --test-notification flag, which is removed.

Scope: main.py, README.md.

Behaviour: in main(), after load_state() and before the monitor loop, send one notification with title 'Support bot started' and body 'Support bot started.' when ntfy_url is set. It is placed after the state load on purpose: a fatal startup error (bad config or state file) exits before the message, so a Docker restart loop does not send one message per restart. A failed send prints the existing warning and the bot continues. All run modes send it (--once and --confirm included). No customer data in the message.

Remove the --test-notification argument, its handling block, and the now-unused sys import. Update README.md: remove the flag section, mention the startup message under ntfy_url.

Non-goals: a shutdown message; a config key to turn the startup message off; special cases per run mode.

