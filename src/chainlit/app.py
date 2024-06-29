from openai import AzureOpenAI
import chainlit as cl
from dotenv import load_dotenv
import os
from src.ingestion.report import Report
from src.llm_agents.kpi_extraction.agent import KPIExtractionAgent
from src.llm_agents.kpi_formula_finder.agent import KPIFormulaFinderAgent
from src.llm_agents.kpi_simple_extraction.agent import KPISimpleExtractionAgent
from src.llm_agents.rag.agent import RAGAgent
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
        cl.ChatProfile(
            name="KPI Formula Finder",
            markdown_description="The underlying LLM model is **GPT-4o.",
            icon="https://picsum.photos/300",
        ),
        cl.ChatProfile(
            name="KPI Simple Extraction",
            markdown_description="The underlying LLM model is **GPT-4o.",
            icon="https://picsum.photos/350",
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
            ),
            Select(
                id="Company",
                label="Company",
                values=["ABB", "IBM", "PostFinance", "Raiffeisen", "Siemens"],
                initial_index=0,
            ),
            Select(
                id="Year",
                label="Year of the annual report",
                values=["2023", "2022", "2021"],
                initial_index=0,
            ),

        ]
    ).send()

    cl.user_session.set("company", settings["Company"])
    cl.user_session.set("year", settings["Year"])

@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set("company", settings["Company"])
    cl.user_session.set("year", settings["Year"])

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
    report.get_kpis()
    return report

@cl.step(show_input=True, type="llm", disable_feedback=False)
def get_report(message):
    report_file = Path(f"../../data/{cl.user_session.get("company")}_{cl.user_session.get("year")}.json")
    report = load_report(report_file)
    chat_profile = cl.user_session.get("chat_profile")
    query = message.content
    if chat_profile == "KPI Extractor":
        agent = KPIExtractionAgent(report)
    elif chat_profile == "Simple Chatbot":
        agent = RAGAgent(report)
    elif chat_profile == "KPI Formula Finder":
        agent = KPIFormulaFinderAgent()
    elif chat_profile == "KPI Simple Extraction":
        agent = KPISimpleExtractionAgent(report, top_k=50)


    message = agent.complete(query)
    
    response = cl.Message(content=message)
    
    return response

@cl.on_message
async def on_message(message: cl.Message):
    message = get_report(message)
    await message.send()
