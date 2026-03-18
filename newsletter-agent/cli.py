from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect web articles and build a curated biweekly newsletter.",
    )
    parser.add_argument(
        "--config",
        default="sources.json",
        help="Path to the JSON source configuration file.",
    )
    parser.add_argument(
        "--output",
        default="newsletter.md",
        help="Path to the Markdown newsletter output file.",
    )
    parser.add_argument(
        "--model",
        default="gpt-5",
        help=(
            "Model used for summarization. For Azure OpenAI, this should match "
            "your deployment name if AZURE_OPENAI_DEPLOYMENT is not set."
        ),
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to an env file with variables like OPENAI_API_KEY.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    from newsletter_agent.agent import NewsletterAgent
    from newsletter_agent.config import load_env_file, load_sources

    load_env_file(args.env_file)
    sources = load_sources(args.config)
    agent = NewsletterAgent(model=args.model)
    newsletter = agent.run(sources=sources, output_path=args.output)
    print(
        f"Wrote {len(newsletter.articles)} summarized articles to {args.output} "
        f"for {newsletter.period_label}."
    )


if __name__ == "__main__":
    main()
