#!/usr/bin/env python3
"""
IMAP Email Monitor and Auto-Reply Script with OpenAI Integration
Monitors multiple folders for new emails and uses OpenAI to generate intelligent support responses.
"""
import json
import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from imap_tools import AND
from imap_tools import MailBox
from openai import OpenAI


# Load configuration from JSON file
def load_config():
    """Load configuration from config.json file."""
    config_path = "config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    with open(config_path, "r") as f:
        return json.load(f)


# Load configuration
CONFIG = load_config()

# Initialize OpenAI client
client = OpenAI()


def load_documentation(file_path):
    """Load documentation content from file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    else:
        return "Documentation file not found."


def load_state():
    """Load the state file containing processed email UIDs per folder."""
    if os.path.exists(CONFIG["state_file"]):
        with open(CONFIG["state_file"], "r") as f:
            state = json.load(f)
            # Ensure each folder has an entry
            for folder in CONFIG["folders"]:
                if folder not in state:
                    state[folder] = {"processed_uids": []}
            return state
    # Initialize state for all folders
    return {folder: {"processed_uids": []} for folder in CONFIG["folders"]}


def save_state(state):
    """Save the state file with processed email UIDs per folder."""
    with open(CONFIG["state_file"], "w") as f:
        json.dump(state, f, indent=2)


def generate_reply_content(original_email, folder_name):
    """
    Use OpenAI to generate an intelligent support response.

    Args:
        original_email: MailMessage object from imap_tools
        folder_name: Name of the folder being processed

    Returns:
        dict with 'subject', 'body', and optionally 'html' keys
    """
    try:
        # Get folder-specific configuration
        folder_config = CONFIG["folders"].get(folder_name, {})
        documentation_file = folder_config.get("documentation_file")
        custom_prompt = folder_config.get("prompt", "")

        # Load documentation if available
        documentation = ""
        if documentation_file:
            documentation = load_documentation(documentation_file)

        # Format the custom prompt with company info
        custom_prompt = custom_prompt.format(
            company_name=CONFIG.get("company_name", "Our Company"),
            support_email=CONFIG.get("support_email", "support@company.com"),
        )

        # Create the prompt for the LLM
        prompt = f"""
{custom_prompt}

Documentation:
{documentation}

Customer Email:
From: {original_email.from_}
Subject: {original_email.subject}
Message:
```
{original_email.text or original_email.html}
```

Please write a helpful and professional response to this customer email. Make sure to:

1. Address their specific questions or concerns.
2. Provide clear and actionable information based on the documentation.
3. Maintain a friendly and professional tone, but don't be condescending or saccharine.
4. Include any relevant links or resources.
5. Take the conversation history into account.
6. Do not use em- or en-dashes. Use normal dashes.
7. Don't sign emails.
"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model=CONFIG["model"],
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful customer support agent. Always be professional, empathetic, and solution-oriented.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        # Extract the generated response
        reply_body = response.choices[0].message.content

        return {
            "subject": f"Re: {original_email.subject}",
            "body": reply_body,
            "html": None,  # You could convert to HTML if needed
        }

    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        # Fallback to a generic response if AI fails
        return {
            "subject": f"Re: {original_email.subject}",
            "body": f"""Dear {original_email.from_},

Thank you for contacting {CONFIG.get("company_name", "Our Company")} support.

We have received your email and are currently experiencing technical difficulties with our automated response system.
A human support agent will review your message and respond within 24 hours.

We apologize for any inconvenience.

Best regards,
{CONFIG.get("company_name", "Our Company")} Support Team
{CONFIG.get("support_email", "support@company.com")}""",
            "html": None,
        }


def send_reply(original_email, reply_content):
    """Send a reply to the original email with proper headers."""
    # Create message
    msg = MIMEMultipart("mixed")

    # Set headers for proper threading
    msg["Subject"] = reply_content["subject"]
    msg["From"] = CONFIG["email"]
    msg["To"] = original_email.from_
    msg["In-Reply-To"] = original_email.headers.get("message-id", [""])[0]
    msg["References"] = original_email.headers.get("message-id", [""])[0]

    # Add body
    body = MIMEMultipart("alternative")
    body.attach(MIMEText(reply_content["body"], "plain"))

    if reply_content.get("html"):
        body.attach(MIMEText(reply_content["html"], "html"))

    msg.attach(body)

    # Optional: Include original message as attachment
    # Uncomment if you want to include the original message
    # original_msg = MIMEMessage(original_email.obj)
    # original_msg['Content-Disposition'] = 'attachment'
    # msg.attach(original_msg)

    # Send email
    with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"]) as server:
        server.starttls()
        server.login(CONFIG["email"], CONFIG["password"])
        server.send_message(msg)

    print(f"Reply sent to {original_email.from_} for: {original_email.subject}")


def process_new_emails(mailbox, folder_name, folder_state):
    """Check for new emails and process them for a specific folder."""
    processed_count = 0

    # Fetch all emails in the monitored folder
    for msg in mailbox.fetch(AND(all=True)):
        # Check if we've already processed this email
        if msg.uid not in folder_state["processed_uids"]:
            print(f"\nNew email detected in '{folder_name}':")
            print(f"  From: {msg.from_}")
            print(f"  Subject: {msg.subject}")
            print(f"  Date: {msg.date}")

            try:
                # Generate reply content using folder-specific configuration
                reply_content = generate_reply_content(msg, folder_name)

                # Send the reply
                # send_reply(msg, reply_content)

                # Mark as processed
                folder_state["processed_uids"].append(msg.uid)
                processed_count += 1

            except Exception as e:
                print(f"Error processing email {msg.uid}: {str(e)}")

    return processed_count


def main():
    """Main monitoring loop."""
    print("Starting AI-powered email support monitor...")
    print(f"Server: {CONFIG['imap_server']}")
    print(f"Account: {CONFIG['email']}")
    print(f"Monitoring folders: {', '.join(CONFIG['folders'].keys())}")
    print(f"Check interval: {CONFIG['check_interval']} seconds")
    print(f"AI Model: {CONFIG['model']}")
    print(f"Company: {CONFIG.get('company_name', 'Not specified')}")
    print("-" * 50)

    # Test OpenAI connection
    try:
        client.models.retrieve(CONFIG["model"])
        print("✓ OpenAI API connection successful")
    except Exception as e:
        print(f"✗ OpenAI API error: {str(e)}")
        print("Please check your API key and model name")
        return

    state = load_state()

    while True:
        try:
            # Connect to mailbox
            with MailBox(CONFIG["imap_server"]).login(
                CONFIG["email"], CONFIG["password"]
            ) as mailbox:
                total_processed = 0

                # Process each configured folder
                for folder_name in CONFIG["folders"]:
                    try:
                        # Select folder
                        mailbox.folder.set(folder_name)

                        # Process new emails for this folder
                        processed = process_new_emails(
                            mailbox, folder_name, state[folder_name]
                        )
                        total_processed += processed

                        if processed > 0:
                            print(
                                f"  Processed {processed} email(s) in '{folder_name}'"
                            )

                    except Exception as e:
                        print(f"\nError processing folder '{folder_name}': {str(e)}")
                        continue

                if total_processed > 0:
                    save_state(state)
                    print(
                        f"\nTotal: Processed {total_processed} new email(s) across all folders"
                    )
                else:
                    print(
                        f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No new emails in any folder"
                    )

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Will retry in next interval...")

        # Wait before next check
        time.sleep(CONFIG["check_interval"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
