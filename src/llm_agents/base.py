import json
import os
from abc import ABC, abstractmethod
from typing import Literal

from dotenv import load_dotenv
from langchain.docstore.document import Document
from openai import AzureOpenAI
from pydantic import BaseModel

from src.ingestion.report import Report

load_dotenv()


class Prompt(BaseModel):
    role: Literal["system", "user"]
    content: str


azure_client = AzureOpenAI(
    api_key=os.getenv("API-KEY"),
    api_version=os.getenv("API-VERSION"),
    azure_endpoint=os.getenv("AZURE-ENDPOINT"),
)


class AgentTemplate(ABC):
    def __init__(self, report: Report = None):
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
            model=os.getenv("COMPLETION-MODEL")
        )
        return resp.choices[0].message.content
