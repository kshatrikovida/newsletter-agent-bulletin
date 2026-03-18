from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from newsletter_agent.fetcher import WebFetcher
from newsletter_agent.models import Article, Newsletter, SourceConfig
from newsletter_agent.renderer import render_markdown
from newsletter_agent.summarizer import ArticleSummarizer


class NewsletterAgent:
    def __init__(self, model: str = "gpt-5") -> None:
        self.fetcher = WebFetcher()
        self.summarizer = ArticleSummarizer(model=model)

    def run(self, sources: list[SourceConfig], output_path: str | Path) -> Newsletter:
        articles: list[Article] = []

        for source in sources:
            for article in self.fetcher.fetch_source_articles(source):
                enriched = self.fetcher.enrich_article_content(article)
                summarized = self.summarizer.summarize(enriched)
                articles.append(summarized)

        newsletter = Newsletter(
            title="Biweekly Research Brief",
            period_label=self._period_label(),
            articles=articles,
        )

        output = render_markdown(newsletter)
        Path(output_path).write_text(output, encoding="utf-8")
        return newsletter

    def _period_label(self) -> str:
        today = datetime.now(timezone.utc).date()
        start = today - timedelta(days=13)
        return f"{start.isoformat()} to {today.isoformat()}"
