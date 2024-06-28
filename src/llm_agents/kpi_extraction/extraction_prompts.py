from pydantic import BaseModel


class ExtractionPrompt(BaseModel):
    kpi_name: str
    prompt: str