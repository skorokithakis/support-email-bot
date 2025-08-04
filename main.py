#!/usr/bin/env python3
"""
IMAP Email Monitor and Auto-Reply Script with OpenAI Integration
Monitors multiple folders for new emails and uses OpenAI to generate intelligent support responses.
"""

import argparse
import json
import os
import smtplib
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from imap_tools import AND
from imap_tools import MailBox
from openai import OpenAI

UTC = timezone.utc


# Load configuration from JSON file
def load_config(config_path="config.json"):
    """Load configuration from specified JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    with open(config_path, "r") as f:
        return json.load(f)


# Initialize OpenAI client (will be set after loading config)
client = None


def load_documentation(file_path, config_path):
    """Load documentation content from file."""
    # Make documentation file path relative to config file directory
    config_dir = os.path.dirname(os.path.abspath(config_path))
    doc_file_path = os.path.join(config_dir, file_path)

    if os.path.exists(doc_file_path):
        with open(doc_file_path, "r") as f:
            return f.read()
    else:
        return "Documentation file not found."


def load_state(config_path):
    """Load the state file containing processed email UIDs per folder."""
    # Make state file path relative to config file directory
    config_dir = os.path.dirname(os.path.abspath(config_path))
    state_file_path = os.path.join(config_dir, CONFIG["state_file"])

    if os.path.exists(state_file_path):
        with open(state_file_path, "r") as f:
            state = json.load(f)
            # Ensure each folder has an entry
            for folder in CONFIG["folders"]:
                if folder not in state:
                    state[folder] = {"processed_uids": []}
            return state
    # Initialize state for all folders
    return {folder: {"processed_uids": []} for folder in CONFIG["folders"]}


def save_state(state, config_path):
    """Save the state file with processed email UIDs per folder."""
    # Make state file path relative to config file directory
    config_dir = os.path.dirname(os.path.abspath(config_path))
    state_file_path = os.path.join(config_dir, CONFIG["state_file"])

    with open(state_file_path, "w") as f:
        json.dump(state, f, indent=2)


def generate_reply_content(original_email, folder_name, config_path):
    """
    Use OpenAI to generate an intelligent support response.

    Args:
        original_email: MailMessage object from imap_tools
        folder_name: Name of the folder being processed
        config_path: Path to the config file

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
            documentation = load_documentation(documentation_file, config_path)

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
8. DO NOT assume things, and DO NOT say you have checked things you haven't. If you don't have access to check something, just don't assume or say anything about it. You MUST NEVER make implicit assumptions that might be wrong.
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


def confirm_and_send_reply(original_email, reply_content, folder_name):
    """Print the reply and ask for confirmation before sending."""
    print("\n" + "=" * 60)
    print("PROPOSED EMAIL RESPONSE:")
    print("=" * 60)
    print(f"To: {original_email.from_}")
    print(f"From: {CONFIG['email']}")
    print(f"Subject: {reply_content['subject']}")
    print("-" * 60)
    print("Body:")
    print(reply_content["body"])
    print("=" * 60)

    # Ask for confirmation.
    while True:
        response = input("\nSend this email? (y/n): ").strip().lower()
        if response == "y":
            print("Sending...")
            send_reply(original_email, reply_content, folder_name)
            return True
        elif response == "n":
            print("Email cancelled.")
            return False
        else:
            print("Please enter 'y' or 'n'.")


def send_reply(original_email, reply_content, folder_name):
    """Send a reply to the original email with proper headers."""
    # Create message
    msg = MIMEMultipart("mixed")

    # Set headers for proper threading
    msg["Subject"] = reply_content["subject"]
    msg["From"] = CONFIG["email"]
    msg["To"] = original_email.from_
    msg["In-Reply-To"] = original_email.headers.get("message-id", [""])[0]
    msg["References"] = original_email.headers.get("message-id", [""])[0]
    msg["Date"] = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg["Message-ID"] = f"<{datetime.now(UTC).timestamp()}.{CONFIG['email']}>"

    # Add body
    body = MIMEMultipart("alternative")
    body.attach(MIMEText(reply_content["body"], "plain"))

    if reply_content.get("html"):
        body.attach(MIMEText(reply_content["html"], "html"))

    msg.attach(body)

    # Send email
    with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"]) as server:
        server.starttls()
        server.login(CONFIG["email"], CONFIG["password"])
        server.send_message(msg)

    print(f"Reply sent to {original_email.from_} for: {original_email.subject}")

    # Save to the same folder as the original message
    try:
        # Convert message to string for IMAP
        msg_string = msg.as_string()

        # Connect to IMAP to save the sent message
        with MailBox(CONFIG["imap_server"]).login(
            CONFIG["email"], CONFIG["password"]
        ) as mailbox:
            # Set the folder to the same as the original message
            try:
                mailbox.folder.set(folder_name)
            except Exception as e:
                print(f"Warning: Could not access folder '{folder_name}': {str(e)}")
                return

            # Append the message to the same folder as the original
            # Use bytes and timezone-aware datetime to avoid compatibility issues
            mailbox.append(
                msg_string.encode(),
                folder_name,
                dt=datetime.now(UTC),
                flag_set=["\\Seen"],
            )
            print(f"Reply saved to '{folder_name}' folder")

    except Exception as e:
        print(f"Warning: Could not save to folder '{folder_name}': {str(e)}")


def process_new_emails(mailbox, folder_name, folder_state, config_path):
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
                reply_content = generate_reply_content(msg, folder_name, config_path)

                # Send the reply with confirmation
                confirm_and_send_reply(msg, reply_content, folder_name)

                # Mark as processed
                folder_state["processed_uids"].append(msg.uid)
                processed_count += 1

            except Exception as e:
                print(f"Error processing email {msg.uid}: {str(e)}")

    return processed_count


def main(config_path):
    """Main monitoring loop."""
    global client

    # Initialize OpenAI client with API key from config
    if "openai_api_key" not in CONFIG:
        print("Error: 'openai_api_key' not found in configuration file")
        print("Please add your OpenAI API key to the config file")
        return

    client = OpenAI(api_key=CONFIG["openai_api_key"])

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

    state = load_state(config_path)

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
                            mailbox, folder_name, state[folder_name], config_path
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
                    save_state(state, config_path)
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="IMAP Email Monitor and Auto-Reply Script with OpenAI Integration"
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    args = parser.parse_args()

    # Load configuration with specified path
    CONFIG = load_config(args.config)

    try:
        main(args.config)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
