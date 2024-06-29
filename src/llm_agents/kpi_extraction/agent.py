from langchain.docstore.document import Document

from src.llm_agents.base import AgentTemplate

from .prompts import KPI_EXTRACTOR_SYSTEM_PROMPT, KPI_EXTRACTOR_TRIGGER_PROMPT


class KPIExtractionAgent(AgentTemplate):
    @property
    def system(self):
        """System Prompt contains the description of the task the the agent need
        to achieve"""
        return KPI_EXTRACTOR_SYSTEM_PROMPT

    @property
    def trigger(self):
        """Trigger Prompt needs to contain {query} and {context} placeholders."""
        return KPI_EXTRACTOR_TRIGGER_PROMPT

    def _get_prompt(self, query, sources: list[Document]):
        formatted_chunks = self.format_sources(sources)
        return [
            {"role": "system", "content": self.system},
            {
                "role": "user",
                "content": self.trigger.format(query=query, sources=formatted_chunks),
            },
        ]
