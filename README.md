# Support email bot

An automated email support system that monitors IMAP folders and uses AI to generate intelligent customer support responses.

## Features

- Monitors multiple email folders for incoming support requests
- Uses an LLM (via LiteLLM) to generate context-aware responses based on product documentation
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
   - LLM API credentials (`llm_api_key`, or set the `LLM_API_KEY` environment variable which takes precedence)
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

### Email settings
- `email` / `password` / `imap_server` / `imap_port` / `smtp_server` / `smtp_port`: Connection details for your email account.
- `check_interval`: Seconds between inbox checks.
- `state_file`: JSON file used to track processed emails.

### LLM settings
- `model`: A LiteLLM model string (e.g. `anthropic/claude-opus-4-6`). Supports any provider LiteLLM supports.
- `llm_api_key`: API key for the LLM provider. Can also be set via the `LLM_API_KEY` environment variable (takes precedence over the config file value).
- `llm_base_url` (optional): Custom base URL for the LLM API. Can also be set via the `LLM_BASE_URL` environment variable (takes precedence). Leave empty or omit to use the provider's default. Useful for pointing at a self-hosted or proxy upstream.
- `reasoning_effort` (optional): Accepts `"low"`, `"medium"`, or `"high"`. Omit to disable adaptive thinking / extended reasoning.

### Other settings
- `company_name` / `support_email`: Used in response templates.
- `send_emails` (boolean): If `true`, emails will be sent. If `false` or not present, runs in dry-run mode and only prints the replies without sending them.
- `sent_folder` / `sent_folders` (optional): Folder(s) to check for already-sent replies.
- `sent_lookback_days` (optional): How many days back to look in sent folders.

### Per-folder settings
Each key under `folders` corresponds to an IMAP folder name. Each folder entry supports:
- `prompt`: A prompt template for the LLM. Can use `{company_name}` and `{support_email}` placeholders.
- `documentation_file` (optional): Path to a documentation file (relative to the config file) to include as context.
