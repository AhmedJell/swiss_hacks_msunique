import os

from langchain.docstore.document import Document

from src.llm_agents.base import MODEL_NAME, AgentTemplate
from src.llm_agents.kpi_formula_finder.agent import KPIFormulaFinderAgent

from .prompts import KPI_EXTRACTOR_SYSTEM_PROMPT, KPI_EXTRACTOR_TRIGGER_PROMPT


class KPIExtractionAgent(AgentTemplate):
    from src.ingestion.report import Report
    def __init__(self, report: Report, top_k: int = 20):
        super().__init__(report)
        self.top_k = top_k
        self.formula_finder = KPIFormulaFinderAgent()

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

        resp = self.azure_client.chat.completions.create(
            messages=prompt, model=MODEL_NAME, temperature=0
        )

        response = self.parse_json(resp.choices[0].message.content)

        try:
            found = response["KPI"]["result"]["found"]

            if found == "False" or not found:
                formula_json = self.parse_json(self.formula_finder.complete(query))

                sub_sources = []
                for formula in formula_json["formulas"]:
                    queries = [elem["question"] for elem in formula["variables"]]
                    for q in queries:
                        sub_sources.extend(
                            self.report.vectorstore.similarity_search_with_score(
                                k=self.top_k, query=q
                            )
                        )

                sub_sources.sort(key=lambda x: x[1], reverse=True)
                sub_sources: list[Document] = [elem[0] for elem in sub_sources]

                filtered_sources = []
                for source in sub_sources:
                    if source.page_content not in [
                        elem.page_content for elem in filtered_sources
                    ]:
                        filtered_sources.append(source)

                augmented_query = f"""You need to anser the following query:
                
                Main Query:
                ```
                {query}
                ```
                To help you answer it, you may need to anser the following queries: 
                ```
                {'\n'.join(queries)}.
                ```"""
                prompt = self._get_prompt(augmented_query, filtered_sources)
                resp = self.azure_client.chat.completions.create(
                    messages=prompt, model=MODEL_NAME, temperature=0
                )
                response = self.parse_json(resp.choices[0].message.content)

                source_page_numbers = []
                for elem in response["KPI"]["source"]:
                    source_num = eval(elem.replace("source", "")) - 1
                    source_page_numbers.append(
                        sub_sources[source_num].metadata["page_number"]
                    )

                response["KPI"]["source"] = source_page_numbers

        except Exception as e:
            print("Unable to process the request. Error=", e)
            source_page_numbers = []
            for elem in response["KPI"]["source"]:
                source_num = eval(elem.replace("source", "")) - 1
                source_page_numbers.append(sources[source_num].metadata["page_number"])

            response["KPI"]["source"] = source_page_numbers

        return response
