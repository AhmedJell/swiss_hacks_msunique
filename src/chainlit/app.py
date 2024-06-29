from openai import AzureOpenAI
import chainlit as cl
from dotenv import load_dotenv
import os
from src.ingestion.report import Report
from src.llm_agents.kpi_extraction.agent import KPIExtractionAgent
from pathlib import Path
from chainlit.input_widget import Select, Switch, Slider
from langchain.docstore.document import Document 


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="KPI Extractor",
            markdown_description="The underlying LLM model is **GPT-4o.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Simple Chatbot",
            markdown_description="Classic RAG on the documents",
            icon="https://picsum.photos/250",
        ),
    ]

@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-4o"],
                initial_index=0,
            ),
            Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=0,
                min=0,
                max=2,
                step=0.1,
            )
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
def load_report(path: Path) -> cl.Message:
    report = Report.from_json(path)
    return report

@cl.step(show_input=True, type="llm", disable_feedback=False)
def get_report(message):
    report = load_report(Path("../../msunique/Data/ABB/2023.json"))
    documents = report.vectorstore.similarity_search(message.content, k=20)
    if chat_profile == "KPI Extractor":
        agent = KPIExtractionAgent()
    elif chat_profile == "Simple Chatbot":
        pass
    message = agent.complete(query=message.content, chunks=documents)
    response = cl.Message(content=message)
    
    return response

@cl.on_message()
async def on_message(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    message = await get_report(message)
    await message.send()
