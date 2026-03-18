from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SourceConfig:
    name: str
    url: str
    article_selector: str
    title_selector: str
    link_selector: str
    excerpt_selector: str | None = None
    date_selector: str | None = None
    max_articles: int = 5


@dataclass(slots=True)
class Article:
    source_name: str
    title: str
    url: str
    published_at: str | None = None
    excerpt: str | None = None
    content: str | None = None
    summary: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Newsletter:
    title: str
    period_label: str
    articles: list[Article]
