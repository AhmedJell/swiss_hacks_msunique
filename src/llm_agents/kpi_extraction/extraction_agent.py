from openai import AzureOpenAI

from src.llm_agents.kpi_extraction.extraction_prompts import ExtractionPrompt


class KpiExtractor:
    def __init__(
        self,
        azure_config: dict,
        prompt: ExtractionPrompt,
        system_prompt: str,
        formatting_inst: str,
        chunks_prompt: str,
    ) -> None:
        self.azure_client = AzureOpenAI(
            api_key=azure_config["apiKey"],
            api_version=azure_config["apiVersion"],
            azure_endpoint=azure_config["azureEndpoint"],
        )
        self.system_prompt = system_prompt
        self.model_name = azure_config["model"]
        self.prompt = f"{prompt.prompt} \n {formatting_inst} \n {chunks_prompt}"
        

    def extract(self, query, chunks: list[str]):
        prompt = f"{self.prompt} \n {'\n'.join(chunks)}"

        resp = self.azure_client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
        )

        return resp.choices[0].message.content
