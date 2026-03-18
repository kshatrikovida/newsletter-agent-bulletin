# Newsletter Agent: Setup and Flow

## What you need

- Python `3.10+`
- Internet access (to fetch source pages and call the OpenAI API)
- Credentials for either OpenAI (`OPENAI_API_KEY`) or Azure OpenAI
- A source config file (`sources.json`)

## Install

```bash
cd /home/labuser/Desktop/Persistant_Folder/newsletter-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Configure

1. Create an env file:

```bash
cp .env.example .env
```

2. Put your credentials in `.env`:

```bash
# Option A: OpenAI API
OPENAI_API_KEY="your-openai-api-key"

# Option B: Azure OpenAI
AZURE_OPENAI_API_KEY="your-azure-openai-key"
AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
AZURE_OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/v1/"
# or:
# AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
# AZURE_OPENAI_API_VERSION="2024-10-21"
```

3. Copy the sample source config:

```bash
cp sources.example.json sources.json
```

4. Edit `sources.json` with real sites and working CSS selectors.

## Run

```bash
newsletter-agent --config sources.json --output newsletter.md
```

You can also choose a model:

```bash
newsletter-agent --config sources.json --output newsletter.md --model gpt-5
```

Or use a custom env file path:

```bash
newsletter-agent --env-file .env.local --config sources.json --output newsletter.md
```

## Runtime flow

1. CLI entrypoint `newsletter_agent/cli.py` parses flags (`--config`, `--output`, `--model`, `--env-file`) and loads env vars from the env file if it exists.
2. `newsletter_agent/config.py` loads `sources.json` into `SourceConfig` objects.
3. `NewsletterAgent` in `newsletter_agent/agent.py` loops through each source.
4. `WebFetcher.fetch_source_articles()` in `newsletter_agent/fetcher.py`:
   - downloads source listing HTML
   - extracts article cards via CSS selectors
   - builds `Article` objects and deduplicates by URL
5. `WebFetcher.enrich_article_content()` fetches each article page and extracts main text from common content selectors (`article`, `main`, etc.). If fetch fails, it falls back to excerpt/title.
6. `ArticleSummarizer.summarize()` in `newsletter_agent/summarizer.py` sends article text to OpenAI/Azure OpenAI Responses API and stores:
   - `summary`
   - parsed `tags` from the `Tags:` line
7. `render_markdown()` in `newsletter_agent/renderer.py` builds final Markdown:
   - top highlights
   - grouped sections by source
8. `NewsletterAgent.run()` writes the final output to the path from `--output` (default `newsletter.md`).

## Expected output

- A generated markdown file (for example `newsletter.md`)
- Console message with article count and coverage period

## Common issues

- Missing API credentials: summarization calls will fail.
- Bad CSS selectors: no cards parsed from source pages.
- Blocked article pages: content falls back to listing excerpt/title.
- Network errors/rate limits: some articles may be skipped or have limited content.
