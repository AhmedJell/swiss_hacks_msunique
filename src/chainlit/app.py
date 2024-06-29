from openai import AzureOpenAI
import chainlit as cl
from dotenv import load_dotenv
import os
from src.ingestion.report import Report
from src.llm_agents.kpi_extraction.agent import KPIExtractionAgent
from pathlib import Path
from chainlit.input_widget import Select, Switch, Slider


@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            ),
            Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=1,
                min=0,
                max=2,
                step=0.1,
            ),
            Slider(
                id="SAI_Steps",
                label="Stability AI - Steps",
                initial=30,
                min=10,
                max=150,
                step=1,
                description="Amount of inference steps performed on image generation.",
            ),
            Slider(
                id="SAI_Cfg_Scale",
                label="Stability AI - Cfg_Scale",
                initial=7,
                min=1,
                max=35,
                step=0.1,
                description="Influences how strongly your generation is guided to match your prompt.",
            ),
            Slider(
                id="SAI_Width",
                label="Stability AI - Image Width",
                initial=512,
                min=256,
                max=2048,
                step=64,
                tooltip="Measured in pixels",
            ),
            Slider(
                id="SAI_Height",
                label="Stability AI - Image Height",
                initial=512,
                min=256,
                max=2048,
                step=64,
                tooltip="Measured in pixels",
            ),
        ]
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

# Load the environment variables
load_dotenv()

# Define the model name to be used
model_name = os.environ.get("COMPLETION-MODEL")

# Initialize the Azure OpenAI client
azure_client = AzureOpenAI(
    api_key=os.environ.get("API-KEY"),
    api_version=os.environ.get("API-VERSION"),
    azure_endpoint=os.environ.get("AZURE-ENDPOINT"),
)


# Instrument the OpenAI client
cl.instrument_openai()

settings = {
    "model": model_name,
    "temperature": 0,
    # ... more settings
}

@cl.cache
def load_report(path: Path):
    report = Report.from_json(path)
    return report

@cl.on_message
async def on_message(message: cl.Message):
    report = load_report(Path("../msunique/Data/ABB/2023.json"))
    documents = report.vectorstore.similarity_search(message.content, k=10)
    agent = KPIExtractionAgent()
    
    await cl.Message(content=agent.complete(query=message.content, chunks=documents)).send()
