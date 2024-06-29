import os
from abc import ABC, abstractmethod
from typing import Literal

from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

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
    @property
    @abstractmethod
    def system(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def trigger(self):
        raise NotImplementedError

    @abstractmethod
    def _get_prompt(self, *args, **kwargs) -> list[dict]:
        raise NotImplementedError

    def parse_json(self, json_output: str) -> dict:
        parsed_json = {}
        try:
            start_index = json_output.index("{")
            end_index = json_output.rindex("}") + 1
            parsed_json = eval(json_output[start_index:end_index])
        except Exception:
            print("Error: Json Parsing Error!")
        
        return parsed_json

    def complete(self, *args, **kwargs):
        prompt = self._get_prompt(*args, **kwargs)
        resp = azure_client.chat.completions.create(
            messages=prompt,
            model=os.getenv("COMPLETION-MODEL")
        )
        return resp.choices[0].message.content
