import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import MarkdownHeaderTextSplitter

load_dotenv()


@dataclass
class Report:
    company_name: str
    year: str
    texts: list[Document]
    embeddings: list[list[float]]
    metadatas: list[dict]
    vectorstore: FAISS
    kpis: list[dict] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_path):
        path = Path(json_path)
        filename = path.stem #File name needs to be in the format company_year.json
        company_name, year = filename.split("_")

        print("Parsing texts for ", company_name, " ", year, " ...")
        texts, metadatas = cls._get_texts(json_path)

        print("Embedding texts for ", company_name, " ", year, " ...")
        embedding_model = AzureOpenAIEmbeddings(
            model=os.getenv("EMBEDDING-MODEL"),
            api_key=os.getenv("API-KEY"),
            api_version=os.getenv("API-VERSION"),
            azure_endpoint=os.getenv("AZURE-ENDPOINT"),
        )

        embeddings = embedding_model.embed_documents(texts)

        vectorstore = FAISS.from_embeddings(
            text_embeddings=list(zip(texts, embeddings)),
            metadatas=metadatas,
            embedding=embedding_model,
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

        for doc in content:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)

        return texts, metadatas

    @classmethod
    def _load_json(cls, file_path):
        with open(file_path) as file:
            return json.load(file)

    @classmethod
    def _parse_content(cls, json_data) -> list[Document]:
        content = json_data["analyzeResult"]["content"]
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on, strip_headers=False
        ).split_text(content)

        return markdown


if __name__ == "__main__":
    report = Report.from_json(
        "/Users/ramiazouz/projects/swiss_hacks_msunique/msunique/Data/ABB/2021.json"
    )
    print(report)
