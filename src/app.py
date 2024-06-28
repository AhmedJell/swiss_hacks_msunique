from openai import AzureOpenAI
import json
import chainlit as cl
from dotenv import load_dotenv
import os
from src.ingestion.report import Report
from pathlib import Path

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


@cl.on_message
async def on_message(message: cl.Message):
    report = Report.from_json(Path("../msunique/Data/ABB/2023.json"))
    report.vectorstore.query(message.content)
    response = azure_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant supporting data analysts.",
            },
            {"role": "user", "content": message.content},
        ],
        **settings,
    )
    await cl.Message(content=response.choices[0].message.content).send()
