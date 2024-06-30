from langchain.docstore.document import Document

from src.llm_agents.base import MODEL_NAME, AgentTemplate, azure_client
from src.llm_agents.rag.prompts import RAG_SYSTEM_PROMPT, RAG_TRIGGER_PROMPT


class MultiRAGAgent(AgentTemplate):
    def __init__(self, reports):
        self.reports = reports

    @property
    def system(self):
        """System Prompt contains the description of the task the the agent need
        to achieve"""
        return RAG_SYSTEM_PROMPT

    @property
    def trigger(self):
        """Trigger Prompt needs to contain {query} and {context} placeholders."""
        return RAG_TRIGGER_PROMPT

    def _add_tab(self, text):
        return "\n".join("\t" + line for line in text.split("\n"))

    def _format_sources(self, chunks: tuple[Document, str, str]):
        sources = ""
        for i, chunk in enumerate(chunks):
            sources += (
                f"<source{i+1}>\n"
                + f"{chunk[0].page_content.strip()}\n"
                + f"<source{i+1}>\n"
            )
        return sources

    def _format_year_sources(self, chunks: list[(Document, str, str)]):
        companies = sorted(set(chunk[2] for chunk in chunks))
        full_source = ""
        for company in companies:
            company_chunks = [chunk for chunk in chunks if chunk[2] == company]
            full_source += (
                f"<company-{company}>\n"
                + self._add_tab(self._format_sources(company_chunks))
                + f"\n<company-{company}>\n"
            )
        return full_source

    def format_sources(self, chunks: list[(Document, str, str)]):
        # Assumes chunk, year, company format
        years = sorted(set(chunk[1] for chunk in chunks))

        sources = ""
        for year in years:
            year_chunks = [chunk for chunk in chunks if chunk[1] == year]
            sources += (
                f"<year-{year}>\n"
                + self._add_tab(self._format_year_sources(year_chunks))
                + f"\n<year-{year}>\n"
            )
        return sources

    def _get_prompt(self, query, sources: list[Document]):
        formatted_sources = self.format_sources(sources)
        return [
            {"role": "system", "content": self.system},
            {
                "role": "user",
                "content": self.trigger.format(query=query, sources=formatted_sources),
            },
        ]

    def complete(self, query):
        docs = []
        for report in self.reports:
            retrieved_docs = report.vectorstore.similarity_search(k=5, query=query)
            docs.extend(
                [(doc, report.year, report.company_name) for doc in retrieved_docs]
            )

        prompt = self._get_prompt(query, docs)
        resp = azure_client.chat.completions.create(messages=prompt, model=MODEL_NAME)
        return resp.choices[0].message.content
