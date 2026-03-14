"""
Ingest Service — Layer 1
Handles parsing PDFs/TXT files, chunking text, generating embeddings,
and storing them in MongoDB Atlas Vector Store via LlamaIndex.
"""
import os
from pathlib import Path

from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch

from django.conf import settings
from api.document_loaders import extract_text


# Configure LlamaIndex to use local HuggingFace embeddings (not OpenAI)
Settings.embed_model = resolve_embed_model("local:sentence-transformers/all-MiniLM-L6-v2")


# MongoDB collection & index names
DB_NAME = "briefing_generator"
COLLECTION_NAME = "document_chunks"
VECTOR_INDEX_NAME = "vector_index"


def get_vector_store():
    """
    Return a LlamaIndex MongoDB Atlas vector store instance.
    The library reads MONGODB_URI from the environment to create both
    sync and async pymongo clients automatically.
    """
    # Ensure the env var the library expects is set
    os.environ["MONGODB_URI"] = settings.MONGO_URI

    return MongoDBAtlasVectorSearch(
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        vector_index_name=VECTOR_INDEX_NAME,
    )


def ingest_documents(file_paths: list[str], project_id: str) -> dict:
    """
    Full ingestion pipeline:
    1. Parse each file to extract text
    2. Chunk the text with SentenceSplitter
    3. Generate embeddings and store in MongoDB Atlas

    Returns a summary dict with chunk counts.
    """
    llama_docs = []

    for fp in file_paths:
        text = extract_text(fp)
        filename = Path(fp).name
        llama_docs.append(
            LlamaDocument(
                text=text,
                metadata={
                    "filename": filename,
                    "project_id": project_id,
                    "source": fp,
                },
            )
        )

    # Chunk into smaller pieces
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(llama_docs)

    # Store in MongoDB Atlas via LlamaIndex
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
    )

    return {
        "documents_processed": len(file_paths),
        "chunks_created": len(nodes),
        "status": "success",
    }
