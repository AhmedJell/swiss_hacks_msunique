from langchain.docstore.document import Document

from src.llm_agents.base import AgentTemplate

from .prompts import RAG_SYSTEM_PROMPT, RAG_TRIGGER_PROMPT


class RAGAgent(AgentTemplate):
    def __init__(self, report: Document, top_k: int=20):
        super().__init__(report)
    @property
    def system(self):
        """System Prompt contains the description of the task the the agent need
        to achieve"""
        return RAG_SYSTEM_PROMPT

    @property
    def trigger(self):
        """Trigger Prompt needs to contain {query} and {context} placeholders."""
        return RAG_TRIGGER_PROMPT

    def _get_prompt(self, query):
        sources = self.report.vectorstore.similarity_search(k=20, query=query)
        formatted_sources = self.format_sources(sources)
        return [
            {"role": "system", "content": self.system},
            {
                "role": "user",
                "content": self.trigger.format(query=query, sources=formatted_sources),
            },
        ]
