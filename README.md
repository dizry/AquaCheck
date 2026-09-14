# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```

### Enable AI inspection guidance

Set an OpenAI API key before starting the app:

```
$ export OPENAI_API_KEY="your-api-key"
```

The inspector uses `gpt-4o-mini` by default. Set `AQUACHECK_AI_MODEL` to choose another compatible model.

### Save feedback to Google Sheets

The feedback form uses the local SQLite database by default. To persist responses in Google Sheets:

1. Create a Google Sheet and copy its ID from the URL.
2. Create a Google Cloud service account, enable the Google Sheets API, and download its JSON credentials.
3. Share the Google Sheet with the service account email as an Editor.
4. Add these values to Streamlit Cloud under **App settings > Secrets**:

```toml
[google_sheets]
spreadsheet_id = "your-google-sheet-id"
worksheet = "Feedback"

[google_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-certificate-url"
universe_domain = "googleapis.com"
```

Never commit the service-account JSON or private key to GitHub. Once the secrets are saved, redeploy the app and new feedback will appear in the `Feedback` worksheet.
