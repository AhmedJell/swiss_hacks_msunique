import os

from src.llm_agents.base import MODEL_NAME, AgentTemplate

from .prompts import (
    KPI_SIMPLE_EXTRACTION_SYSTEM_PROMPT,
    KPI_SIMPLE_EXTRACTION_TRIGGER_PROMPT,
)


class KPISimpleExtractionAgent(AgentTemplate):

    def __init__(self, report, top_k: int = 20):
        super().__init__(report)
        self.top_k = top_k
    @property
    def system(self):
        """System Prompt contains the description of the task the the agent need
        to achieve"""
        return KPI_SIMPLE_EXTRACTION_SYSTEM_PROMPT

    @property
    def trigger(self):
        """Trigger Prompt needs to contain {query} and {context} placeholders."""
        return KPI_SIMPLE_EXTRACTION_TRIGGER_PROMPT

    def _get_prompt(self, query, sources):
        formatted_sources = self.format_sources(sources)
        return [
            {"role": "system", "content": self.system},
            {
                "role": "user",
                "content": self.trigger.format(query=query, sources=formatted_sources),
            },
        ]
    def complete(self, query):
        sources = self.report.vectorstore.similarity_search(k=self.top_k, query=query)
        prompt = self._get_prompt(query, sources)

        for _ in range(5):
            try:
                resp = self.azure_client.chat.completions.create(
                    messages=prompt, model=MODEL_NAME, temperature=0
                )
                response = self.parse_json(resp.choices[0].message.content)
                response = self.get_kpi_source_pages(response, sources)
                return response
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

        return None

