from __future__ import annotations

from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from newsletter_agent.models import Article, SourceConfig

DEFAULT_TIMEOUT = 20
USER_AGENT = "newsletter-agent/0.1 (+https://example.local)"


class WebFetcher:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_source_articles(self, source: SourceConfig) -> list[Article]:
        html = self._get_text(source.url)
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(source.article_selector)
        articles: list[Article] = []

        for card in cards:
            title_node = card.select_one(source.title_selector)
            link_node = card.select_one(source.link_selector)
            if title_node is None or link_node is None:
                continue

            href = link_node.get("href")
            if not href:
                continue

            article = Article(
                source_name=source.name,
                title=self._clean_text(title_node.get_text(" ", strip=True)),
                url=self._resolve_url(source.url, href),
                published_at=self._extract_text(card, source.date_selector),
                excerpt=self._extract_text(card, source.excerpt_selector),
            )
            articles.append(article)

            if len(articles) >= source.max_articles:
                break

        return self._dedupe_articles(articles)

    def enrich_article_content(self, article: Article) -> Article:
        try:
            html = self._get_text(article.url)
        except (OSError, requests.RequestException, ValueError):
            article.content = article.excerpt
            return article

        soup = BeautifulSoup(html, "html.parser")
        content_selectors = [
            "article",
            "main",
            "[role='main']",
            ".post-content",
            ".entry-content",
            ".article-body",
        ]

        content = ""
        for selector in content_selectors:
            node = soup.select_one(selector)
            if node is None:
                continue

            paragraphs = [
                self._clean_text(p.get_text(" ", strip=True))
                for p in node.select("p")
                if self._clean_text(p.get_text(" ", strip=True))
            ]
            if paragraphs:
                content = "\n".join(paragraphs)
                break

        article.content = content or article.excerpt or article.title
        return article

    def _get_text(self, url: str) -> str:
        if self._is_local_source(url):
            return self._read_local_text(url)

        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _resolve_url(self, base: str, href: str) -> str:
        if self._is_local_source(base):
            return str(self._resolve_local_path(base, href))
        return urljoin(base, href)

    def _is_local_source(self, value: str) -> bool:
        parsed = urlparse(value)
        if parsed.scheme == "file":
            return True
        if parsed.scheme:
            return False
        return True

    def _read_local_text(self, url: str) -> str:
        return self._local_path_from_url(url).read_text(encoding="utf-8")

    def _resolve_local_path(self, base: str, href: str) -> Path:
        href_path = Path(unquote(urlparse(href).path if urlparse(href).scheme == "file" else href))
        if href_path.is_absolute():
            return href_path
        return self._local_path_from_url(base).parent / href_path

    def _local_path_from_url(self, url: str) -> Path:
        parsed = urlparse(url)
        if parsed.scheme == "file":
            return Path(unquote(parsed.path))
        return Path(url).expanduser()

    def _extract_text(self, card: BeautifulSoup, selector: str | None) -> str | None:
        if not selector:
            return None
        node = card.select_one(selector)
        if node is None:
            return None
        return self._clean_text(node.get_text(" ", strip=True)) or None

    def _dedupe_articles(self, articles: Iterable[Article]) -> list[Article]:
        deduped: list[Article] = []
        seen: set[str] = set()

        for article in articles:
            if article.url in seen:
                continue
            seen.add(article.url)
            deduped.append(article)

        return deduped

    @staticmethod
    def _clean_text(value: str) -> str:
        return " ".join(value.split())
