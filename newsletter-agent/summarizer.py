from __future__ import annotations

import os

from newsletter_agent.models import Article


class ArticleSummarizer:
    def __init__(self, model: str = "gpt-5") -> None:
        from openai import AzureOpenAI, OpenAI

        self.client, self.model = self._build_client(
            model=model,
            openai_client_cls=OpenAI,
            azure_client_cls=AzureOpenAI,
        )

    def summarize(self, article: Article) -> Article:
        source_text = article.content or article.excerpt or article.title
        prompt = self._build_prompt(article.title, article.url, source_text)

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        article.summary = response.output_text.strip()
        article.tags = self._extract_tags(article.summary)
        return article

    def _build_prompt(self, title: str, url: str, source_text: str) -> str:
        trimmed_text = source_text[:8000]
        return (
            "You are helping curate a biweekly newsletter.\n"
            "Summarize the article below for busy readers.\n"
            "Return plain text in this exact structure:\n"
            "Summary: 2-3 concise sentences.\n"
            "Why it matters: 1 sentence.\n"
            "Tags: comma-separated short tags.\n\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Article text:\n{trimmed_text}"
        )

    def _extract_tags(self, summary: str) -> list[str]:
        for line in summary.splitlines():
            if not line.lower().startswith("tags:"):
                continue
            raw_tags = line.split(":", 1)[1]
            return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
        return []

    def _build_client(
        self,
        model: str,
        openai_client_cls,
        azure_client_cls,
    ) -> tuple[object, str]:
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_base_url = os.getenv("AZURE_OPENAI_BASE_URL")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        azure_requested = any(
            [azure_api_key, azure_base_url, azure_endpoint, azure_deployment]
        )
        if azure_requested:
            if not azure_api_key:
                raise ValueError(
                    "Azure OpenAI selected, but AZURE_OPENAI_API_KEY is missing."
                )
            if not azure_deployment:
                raise ValueError(
                    "Azure OpenAI selected, but AZURE_OPENAI_DEPLOYMENT is missing. "
                    "Set it to your Azure model deployment name."
                )
            if azure_base_url:
                # For Azure v1-style usage, base URL looks like:
                # https://<resource>.openai.azure.com/openai/v1/
                client = openai_client_cls(api_key=azure_api_key, base_url=azure_base_url)
                return client, azure_deployment

            if not azure_endpoint:
                raise ValueError(
                    "Set AZURE_OPENAI_BASE_URL or AZURE_OPENAI_ENDPOINT for Azure OpenAI."
                )

            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
            client = azure_client_cls(
                api_key=azure_api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
            )
            return client, azure_deployment

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "Missing API credentials. Set OPENAI_API_KEY or Azure OpenAI vars."
            )
        return openai_client_cls(api_key=openai_api_key), model
