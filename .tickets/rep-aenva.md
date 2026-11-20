---
id: rep-aenva
status: closed
deps: []
links: []
created: 2026-11-20T19:34:42Z
type: feature
priority: 2
assignee: Stavros Korokithakis
---
# Add ntfy notification on failure

ready for implementation

Objective: the support bot (main.py) sends an ntfy push notification when something goes wrong, so a human knows to act. Today all errors only print to the log.

Scope: main.py, README.md, config.json.example.

Config: one new optional key, ntfy_url (full topic URL, e.g. https://ntfy.sh/example-topic). If the key is absent or empty, notifications are disabled and the bot starts and behaves exactly as today. It must never refuse to start because of this key. Print whether notifications are enabled in the startup banner (do not print the URL; the topic name is the only secret).

Triggers:
1. An email is given up: in process_new_emails, when the retry count reaches max_retries (the branch that appends to failed_emails). One notification per given-up email. Not on earlier attempts.
2. A cycle starts to fail: in the main loop, when a cycle has a folder-level or connection-level error (the two except blocks in main()) and the previous cycle had none. One in-memory boolean is enough. A continuous fault gives one notification, not one per cycle. If several errors happen in one failing cycle, one notification is enough.

Message: title 'Support bot error'. Body is plain text: what failed, folder name (where applicable), email UID (trigger 1), and the error as exception type name plus text. Error text is cut to about 300 characters.

NO customer data in the message: never include sender, subject or body. For trigger 1, replace any occurrence of the sender address (msg.from_) in the error text with a placeholder before sending, because smtplib.SMTPRecipientsRefused includes the recipient address in its text. Put a short code comment at this point that says why (owner requirement: no PII in notifications).

Transport: one HTTP POST to ntfy_url with urllib.request from the standard library, body = message as UTF-8, Title header, timeout 10 seconds. No new dependency. A notification failure (any exception) is caught inside the notify function, printed, and never propagates. It must not change retry counts or stop the loop. Do not print the URL in that error output.

--test-notification flag: sends one test notification and exits. Exit code non-zero and a clear message if ntfy_url is not configured or the send fails (for this flag only, the failure must be visible, so the send helper needs a way to report success).

State save fix: in process_new_emails, a failed attempt (the except branch) must mark the state as changed so retry_counts and failed_emails are saved in that cycle. Today state is saved only when an email succeeds or a new replied-to ID is seen, so a restart loses the counts and would cause a duplicate notification.

Docs: add ntfy_url to config.json.example and to README.md (what it does, when it fires, that it is optional, that messages contain no sender or subject, and the --test-notification flag).

Non-goals: Telegram or any other channel; ntfy authentication (no token); notifications for fatal startup errors (the outer except around main()); rate limits, grouping, or a 'recovered' message; changes to the retry policy; adding a test framework or automated tests (the repo has none); refactoring unrelated code in main.py.

## Design

Keep it small: one notify helper plus call sites, in main.py (single-file project, keep it that way). Rejected: Telegram (owner chose ntfy), a notification library such as apprise (new dependency for one POST), notifying on every failed attempt (noise; most temporary failures recover). HTTP header values in urllib must be latin-1; the title is a fixed ASCII string, keep any variable text in the body only.

## Acceptance Criteria

With ntfy_url set: a given-up email produces exactly one notification with the error text and without the sender address or subject; a continuous IMAP/folder fault produces one notification, and a new one only after a good cycle. With ntfy_url absent or empty: bot starts and behaves as today. ruff check, ruff format and mypy (per .pre-commit-config.yaml) pass.

