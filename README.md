# Support email bot

An automated email support system that monitors IMAP folders and uses AI to generate intelligent customer support responses.

## Features

- Monitors multiple email folders for incoming support requests
- Uses OpenAI to generate context-aware responses based on product documentation
- Maintains proper email threading for organized conversations
- Tracks processed emails to avoid duplicate responses
- Configurable per-folder documentation and response prompts

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Configure the bot by editing `config.json`:
   - Email server settings (IMAP/SMTP)
   - OpenAI API credentials
   - Folders to monitor with their documentation files
   - Company information

3. Add your product documentation files to the `support_documentation/` directory

## Running

Start the email monitor:
```bash
uv run python main.py
```

The bot will continuously monitor the configured folders and automatically respond to new emails using AI-generated responses based on your documentation.

## Configuration

The `config.json` file controls:
- Email server connection details
- Monitoring intervals
- AI model selection
- Folder-specific documentation and response prompts