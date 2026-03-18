from __future__ import annotations

from collections import defaultdict

from newsletter_agent.models import Article, Newsletter


def render_markdown(newsletter: Newsletter) -> str:
    lines = [
        f"# {newsletter.title}",
        "",
        f"**Coverage:** {newsletter.period_label}",
        "",
        f"Collected {len(newsletter.articles)} articles.",
        "",
        "## Highlights",
        "",
    ]

    for article in newsletter.articles:
        lines.extend(_render_highlight(article))

    grouped: dict[str, list[Article]] = defaultdict(list)
    for article in newsletter.articles:
        grouped[article.source_name].append(article)

    for source_name, items in grouped.items():
        lines.extend(
            [
                "",
                f"## {source_name}",
                "",
            ]
        )
        for article in items:
            lines.extend(_render_article(article))

    return "\n".join(lines).strip() + "\n"


def _render_highlight(article: Article) -> list[str]:
    summary_line = _first_content_line(article.summary, "Summary:")
    return [
        f"- [{article.title}]({article.url})",
        f"  {summary_line}",
    ]


def _render_article(article: Article) -> list[str]:
    lines = [
        f"### [{article.title}]({article.url})",
        "",
    ]

    if article.published_at:
        lines.append(f"- Published: {article.published_at}")
    if article.tags:
        lines.append(f"- Tags: {', '.join(article.tags)}")
    lines.append("")

    if article.summary:
        lines.append(article.summary)
        lines.append("")
    elif article.excerpt:
        lines.append(article.excerpt)
        lines.append("")

    return lines


def _first_content_line(summary: str | None, prefix: str) -> str:
    if not summary:
        return "No summary available."

    for line in summary.splitlines():
        if line.startswith(prefix):
            return line
    return summary.splitlines()[0] if summary.splitlines() else "No summary available."
