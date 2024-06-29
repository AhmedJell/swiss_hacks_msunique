import json
import os
from abc import ABC, abstractmethod
from typing import Literal

from dotenv import load_dotenv
from langchain.docstore.document import Document
from openai import AzureOpenAI
from pydantic import BaseModel

load_dotenv()


class Prompt(BaseModel):
    role: Literal["system", "user"]
    content: str


azure_client = AzureOpenAI(
    api_key="a096090373464949980ad13a8291afa3",
    api_version="2024-02-01",
    azure_endpoint="https://regioneastus2.openai.azure.com/",
)

MODEL_NAME = "gpt-4o-East-US2"

class AgentTemplate(ABC):
    def __init__(self, report = None):
        self.report = report

    @property
    @abstractmethod
    def system(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def trigger(self):
        raise NotImplementedError
    
    @property
    def azure_client(self):
        return azure_client

    @abstractmethod
    def _get_prompt(self, *args, **kwargs) -> list[dict]:
        raise NotImplementedError

    def parse_json(self, json_output: str) -> dict:
        parsed_json = {}
        try:
            start_index = json_output.index("{")
            end_index = json_output.rindex("}") + 1
            parsed_json = json.loads(json_output[start_index:end_index])
        except Exception as e:
            print("Error: Json Parsing Error! ", e)
        
        return parsed_json
    
    def format_sources(self, chunks: list[Document]):
        sources = ""
        for i, chunk in enumerate(chunks):
            sources += f"<source{i+1}>{chunk.page_content}<source{i+1}>\n"
        return sources
    
    def complete(self, *args, **kwargs):
        prompt = self._get_prompt(*args, **kwargs)
        resp = azure_client.chat.completions.create(
            messages=prompt,
            model=MODEL_NAME
        )
        return resp.choices[0].message.content

    def get_kpi_source_pages(self, response, sources):
        values = []
        for elem in response["KPI"]["values"]:
            source_num = eval(elem['source'].replace("source", "")) - 1
            elem['source'] = sources[source_num].metadata["page_number"]
            values.append(
                elem
            )

        response["KPI"]["values"] = values

        return response