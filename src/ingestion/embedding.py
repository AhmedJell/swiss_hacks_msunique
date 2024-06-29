import os
from typing import List

from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer


class CombinedEmbedding(Embeddings):
    azure_embeddings = AzureOpenAIEmbeddings(
        model=os.getenv("EMBEDDING-MODEL"),
        api_key=os.getenv("API-KEY"),
        api_version=os.getenv("API-VERSION"),
        azure_endpoint=os.getenv("AZURE-ENDPOINT"),
    )

    tf_embeddings = TfidfVectorizer()

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        azure_embeddings = self.azure_embeddings.embed_documents(texts)
        self.tf_embeddings = self.tf_embeddings.fit(texts)

        tf_embeddings = self.tf_embeddings.transform(texts).toarray().tolist()

        embeddings = [
            azure_embedding + tf_embedding
            for azure_embedding, tf_embedding in zip(azure_embeddings, tf_embeddings)
        ]

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        azure_embedding = [
            (1-self.alpha) * elem for elem in
            self.azure_embeddings.embed_query(text)
        ]

        tf_embedding = [
            self.alpha * elem for elem in self.tf_embeddings.transform([text])
            .toarray()[0]
        ]

        return azure_embedding + tf_embedding
