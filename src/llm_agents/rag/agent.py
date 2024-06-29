from langchain.docstore.document import Document

from src.llm_agents.base import AgentTemplate

from .prompts import RAG_SYSTEM_PROMPT, RAG_TRIGGER_PROMPT


class RAGAgent(AgentTemplate):
    @property
    def system(self):
        """System Prompt contains the description of the task the the agent need
        to achieve"""
        return RAG_SYSTEM_PROMPT

    @property
    def trigger(self):
        """Trigger Prompt needs to contain {query} and {context} placeholders."""
        return RAG_TRIGGER_PROMPT

    def format_sources(self, chunks: list[Document]):
        sources = ""
        for i, chunk in enumerate(chunks):
            sources += f"<source{i+1}>{chunk.page_content}<source{i+1}>\n"
        return sources

    def _get_prompt(self, question, sources: list[Document]):
        formatted_sources = self.format_sources(sources)
        return [
            {"role": "system", "content": self.system},
            {
                "role": "user",
                "content": self.trigger.format(question=question, sources=formatted_sources),
            },
        ]
