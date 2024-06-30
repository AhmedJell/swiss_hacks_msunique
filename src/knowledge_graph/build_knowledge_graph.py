from llama_index.core import (
    PropertyGraphIndex,
)
from llama_index.core.indices.property_graph import (
    ImplicitPathExtractor,
    SchemaLLMPathExtractor,
)
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

from src.knowledge_graph.schema import entities, relations, validation_schema


def neo4j_pg_store(
    user,
    password,
    uri,
):
    return Neo4jPropertyGraphStore(
        username=user,
        password=password,
        url=uri,
    )


def build_knowledge_graph(llm, docs, pg_store):
    kg_extractor = SchemaLLMPathExtractor(
        llm=llm,
        possible_entities=entities,
        possible_relations=relations,
        kg_validation_schema=validation_schema,
        strict=True,
        max_triplets_per_chunk=50,
    )
    return PropertyGraphIndex.from_documents(
        docs,
        property_graph_store=pg_store,
        kg_extractors=[kg_extractor, ImplicitPathExtractor()],
        show_progress=True,
    )
