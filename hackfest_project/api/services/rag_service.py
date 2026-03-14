"""
RAG Agent Service — Layer 2
Uses LlamaIndex to retrieve relevant chunks from MongoDB Atlas,
then calls Groq LLM to generate Tailwind HTML presentation slides.
"""
import os

from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.core.llms import ChatMessage, MessageRole

from django.conf import settings

from api.services.ingest_service import get_vector_store
from api.prompts import SLIDE_GENERATION_SYSTEM_PROMPT, HTML_EDIT_SYSTEM_PROMPT
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


def generate_slides_html(query: str, project_id: str, existing_html: str | None = None) -> str:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from the vector store
    2. Build a prompt with the context
    3. Call Groq LLM to generate Tailwind HTML slides
    4. Return the raw HTML string (no JSON parsing)

    If existing_html is passed, the LLM is instructed to UPDATE
    content while preserving the layout/design.
    """
    # Step 1: Retrieve context
    chunks = retrieve_context(query, project_id)
    context_text = "\n\n---\n\n".join(chunks) if chunks else "No relevant documents found. Generate based on general knowledge."

    # Step 2: Build prompt
    user_prompt = f"""CONTEXT FROM UPLOADED DOCUMENTS:
{context_text}

USER QUERY: {query}
"""

    # Step 3: Choose system prompt based on mode
    if existing_html:
        system_prompt = HTML_EDIT_SYSTEM_PROMPT
        user_prompt += f"""

EXISTING PRESENTATION HTML (UPDATE THIS):
{existing_html}

Update the content based on the new query and context above.
Keep the same visual design and layout structure.
"""
    else:
        system_prompt = SLIDE_GENERATION_SYSTEM_PROMPT
        user_prompt += "\n\nGenerate the presentation slides now:"

    # Step 4: Call Groq LLM
    llm = get_llm()
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
        ChatMessage(role=MessageRole.USER, content=user_prompt),
    ]
    response = llm.chat(messages)

    # Step 5: Clean up response
    response_text = response.message.content.strip()

    # Remove markdown code fences if the LLM wraps them
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

    return response_text
