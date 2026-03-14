"""
RAG Agent Service — Layer 2
Uses LlamaIndex to retrieve relevant chunks from MongoDB Atlas,
then calls Groq LLM to generate a structured SlideDeck JSON.
"""
import json
import os

from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.groq import Groq

from django.conf import settings

from api.schemas import SlideDeck, Slide, SlideElement, AnimationType, TransitionType
from api.services.ingest_service import get_vector_store
from api.prompts import SLIDE_GENERATION_SYSTEM_PROMPT, UPDATE_MODE_INSTRUCTION
from api.llm_client import get_llm


def retrieve_context(query: str, project_id: str, top_k: int = 10) -> list[str]:
    """
    Retrieve the most relevant document chunks for a query
    from MongoDB Atlas Vector Search.
    """
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )

    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)

    chunks = []
    for node in nodes:
        source = node.metadata.get("filename", "Unknown")
        chunks.append(f"[Source: {source}]\n{node.text}")

    return chunks


def generate_slide_schema(query: str, project_id: str, existing_schema: dict | None = None) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from the vector store
    2. Build a prompt with the context
    3. Call Groq LLM to generate structured slide JSON
    4. Validate with Pydantic and return

    If existing_schema is passed, the LLM is instructed to UPDATE
    content while preserving animation metadata (Animation Lock).
    """
    # Step 1: Retrieve context
    chunks = retrieve_context(query, project_id)
    context_text = "\n\n---\n\n".join(chunks) if chunks else "No relevant documents found. Generate based on general knowledge."

    # Step 2: Build prompt
    user_prompt = f"""CONTEXT FROM UPLOADED DOCUMENTS:
{context_text}

USER QUERY: {query}
"""

    # If updating an existing schema, add animation lock instructions
    if existing_schema:
        user_prompt += f"""

EXISTING PRESENTATION (UPDATE THIS):
{json.dumps(existing_schema, indent=2)}

IMPORTANT: You are UPDATING this existing presentation. 
- Modify the text content based on the new query/context.
- PRESERVE all animation types, animation delays, and transitions EXACTLY as they are.
- Only change animations if the user explicitly asks for animation changes.
- You may add or remove slides if needed, but keep existing slide animations intact.
"""

    user_prompt += "\n\nGenerate the presentation JSON now:"

    # Step 3: Call Groq LLM
    llm = get_llm()
    sys_prompt = SLIDE_GENERATION_SYSTEM_PROMPT if not existing_schema else SLIDE_GENERATION_SYSTEM_PROMPT + UPDATE_MODE_INSTRUCTION

    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=sys_prompt),
        ChatMessage(role=MessageRole.USER, content=user_prompt),
    ]
    response = llm.chat(messages)

    # Step 4: Parse and validate
    response_text = response.message.content.strip()

    # Clean up if the LLM wraps in markdown code blocks
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

    raw_json = json.loads(response_text)

    # Validate with Pydantic
    deck = SlideDeck(**raw_json)

    return deck.model_dump()
