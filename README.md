# Air Quality Service

## API access

The health check at `/` is public. Requests to `/api/air-quality/latest` require
the shared API key configured in the `AIR_QUALITY_API_TOKEN` environment
variable. If the variable is missing, the data endpoint returns `503` rather
than allowing unauthenticated access.

Generate a secret token:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

For local development, copy `.env.example` to `.env`, then replace the example
value with the generated token. The service loads `.env` automatically; `.env`
is ignored by Git and must not be committed. Install the project requirements
and start or restart the service:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Send the token in the `X-API-Key` header when requesting data:

```bash
curl -H "X-API-Key: paste-your-token-here" \
  "http://127.0.0.1:8000/api/air-quality/latest?location=London"
```

Keep the token secret, do not commit it to source control, and use HTTPS when
accessing the service over a network.
