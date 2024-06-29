import json
import os
import pickle
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from src.llm_agents.kpi_simple_extraction.agent import KPISimpleExtractionAgent

import pandas as pd
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from tqdm import tqdm


load_dotenv()

kpi_questions = [
    "What are the company's total assets?",
    "What are the company's current assets?",
    "What is the cash and cash equivalents of the company?",
    "What are the inventories of the company?",
    "What are the company's current liabilities?",
    "What is the company's total equity?",
    "What is the company's total revenue?",
    "What is the company's gross profit?",
    "What is the company's EBITDA?",
    "What is the company's EBIT?",
    "What is the company's net income?",
    "What are the company's cash flow from operations?",
    "What are the company's cash flow from investing?",
    "What are the company's cash flow from financing?",
]

page_number_pattern = r'<!-- PageNumber="(\d+)" -->'


def remove_page_number(text):
    return re.sub(page_number_pattern, "", text)


page_header_pattern = r'<!-- PageHeader="[^"]*" -->'


def remove_page_header(text):
    """Removes the page header pattern from the given text."""
    return re.sub(page_header_pattern, "", text)


markdown_patterns = {
    "#": "Header 1",
    "##": "Header 2",
    "###": "Header 3",
}

compiled_patterns = {re.compile(f"^{k} (.+)"): v for k, v in markdown_patterns.items()}

vectorstore_path = Path(__file__).parent.parent.parent / "data" / "vectorstore"


@dataclass
class Report:
    company_name: str
    year: str
    texts: list[Document]
    embeddings: list[list[float]]
    metadatas: list[dict]
    vectorstore: FAISS
    kpis: pd.DataFrame = field(default_factory=pd.DataFrame)

    @classmethod
    def from_json(cls, json_path):
        path = Path(json_path)
        filename = path.stem  # File name needs to be in the format company_year.json
        company_name, year = filename.split("_")

        print("Parsing texts for ", company_name, " ", year, " ...")
        texts, metadatas = cls._get_texts(json_path)

        embedding_model = AzureOpenAIEmbeddings(
            model=os.getenv("EMBEDDING-MODEL"),
            api_key=os.getenv("API-KEY"),
            api_version=os.getenv("API-VERSION"),
            azure_endpoint=os.getenv("AZURE-ENDPOINT"),
        )
        save_dir = vectorstore_path / company_name / year
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
            print("Embedding texts for ", company_name, " ", year, " ...")
            embeddings = embedding_model.embed_documents(texts)

            vectorstore = FAISS.from_embeddings(
                text_embeddings=list(zip(texts, embeddings)),
                metadatas=metadatas,
                embedding=embedding_model,
                distance_strategy=DistanceStrategy.COSINE,
            )

            # Save the embeddings with pickle
            with open(save_dir / "embeddings.pkl", "wb") as file:
                pickle.dump(embeddings, file)

            vectorstore.save_local(save_dir / "vectorstore")

        else:
            print("Loading embeddings for ", company_name, " ", year, " ...")
            with open(save_dir / "embeddings.pkl", "rb") as file:
                embeddings = pickle.load(file)

            vectorstore = FAISS.load_local(
                save_dir / "vectorstore",
                embeddings=embedding_model,
                allow_dangerous_deserialization=True,
            )

        return cls(
            company_name=company_name,
            year=year,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            vectorstore=vectorstore,
        )

    @classmethod
    def _get_texts(cls, json_path):
        json_data = cls._load_json(json_path)
        content = cls._parse_content(json_data)
        texts = []
        metadatas = []

        for elem in content:
            texts.append(elem["text"])
            metadatas.append(elem["metadata"])

        return texts, metadatas

    @classmethod
    def _load_json(cls, file_path):
        with open(file_path) as file:
            return json.load(file)

    @classmethod
    def _parse_content(cls, json_data) -> list[dict]:
        content = []
        for page in json_data["analyzeResult"]["pages"]:
            headers = defaultdict(list)
            lines = []
            for line in page["lines"]:
                line_content = line["content"]
                for pattern, header in compiled_patterns.items():
                    match = pattern.match(line_content)
                    if match:
                        headers[header].append(match.group(1))
                lines.append(line_content)

            text = "\n".join(lines)
            text = remove_page_number(text)
            text = remove_page_header(text)

            content.append(
                {
                    "metadata": {
                        "page_number": page["pageNumber"],
                        "markdown_header": dict(headers),
                    },
                    "text": text,
                }
            )

        return content

    def get_kpis(self) -> pd.DataFrame:
        agent = KPISimpleExtractionAgent(self)
        output = {
            "questions": [
                {"question": question, "response": agent.complete(question)}
                for question in tqdm(kpi_questions)
            ]
        }
        df = pd.DataFrame(output["questions"])
        df = df.assign(**df["response"].apply(pd.Series))
        df = df.query("not response.isna()")
        df = df.assign(**df["KPI"].apply(pd.Series))
        df = df.explode("values")
        df = df.query("not values.isna()")
        df = df.assign(**df["values"].apply(pd.Series))
        df.found = df.found.apply(lambda x: 1 if x == "True" or x else 0)
        df.drop(columns=["response", "KPI", "values"], inplace=True)
        df_kpis = df.sort_values("source").reset_index(drop=True)

        save_path = (
            Path(__file__).parent.parent.parent
            / "data"
            / "kpis"
            / f"{self.company_name}_{self.year}.json"
        )
        if not save_path.parent.exists():
            save_path.parent.mkdir(parents=True)

        df_kpis.to_json(save_path, orient="records")

        self.kpis = df_kpis
        
        return df_kpis


if __name__ == "__main__":
    report = Report.from_json(
        "/Users/ramiazouz/projects/swiss_hacks_msunique/msunique/Data/ABB/2021.json"
    )
    print(report)
