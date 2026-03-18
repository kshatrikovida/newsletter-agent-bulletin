# Newsletter Agent

`newsletter-agent` is a small Python project that collects articles from selected web resources, summarizes them with OpenAI, and writes a curated biweekly newsletter in Markdown.

## Features

- Fetches article listings with `requests`
- Parses HTML with `BeautifulSoup`
- Summarizes each article with the OpenAI Python SDK
- Produces a Markdown newsletter grouped by source
- Uses a JSON config so you can tune selectors per source

## Quickstart

1. Create and activate a virtual environment.
2. Install the project:

```bash
pip install -r requirements.txt
pip install -e .
```

If your packaging tools are old, this project now includes a minimal `setup.py` so editable installs can still work.

3. Create an env file from the example:

```bash
cp .env.example .env
```

4. Put your credentials in `.env`:

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

5. Copy the sample source configuration and update selectors as needed:

```bash
cp sources.example.json sources.json
```

6. Run the agent:

```bash
newsletter-agent --config sources.json --output newsletter.md
```

The CLI loads `.env` by default. You can override this:

```bash
newsletter-agent --env-file .env.local --config sources.json --output newsletter.md
```

## Configuration

Each source in `sources.json` describes how to extract article cards from a listing page:

```json
{
  "name": "OpenAI News",
  "url": "https://openai.com/news/",
  "article_selector": "article",
  "title_selector": "h3 a, h2 a, a[href]",
  "link_selector": "h3 a, h2 a, a[href]",
  "excerpt_selector": "p",
  "date_selector": "time, [datetime]",
  "max_articles": 5
}
```

Optional keys:

- `excerpt_selector`: Pulls teaser text from the listing page.
- `date_selector`: Pulls a published date string if available.
- `max_articles`: Limits how many articles to include from that source.

## Notes

- The agent summarizes the article page itself when it can fetch it successfully.
- If a source blocks article-page scraping, the agent falls back to the listing-page excerpt.
- CSS selectors vary per site, so the sample file is meant to be adapted.
- The default model is `gpt-5`, but you can override it with `--model`.
- For Azure OpenAI, the effective model comes from `AZURE_OPENAI_DEPLOYMENT` (deployment name).

## Official OpenAI reference

This project uses the current OpenAI Python SDK pattern shown in the official docs with `from openai import OpenAI` and `client.responses.create(...)`:

- https://platform.openai.com/docs/quickstart/step-1-setting-up-python
