"""
LLM Client setup and configuration.
Modeled after the reference `llm_client.py` architecture.
Abstracts away the specific LLM provider initialization from our core services.
"""
from django.conf import settings
from llama_index.llms.groq import Groq


def get_llm():
    """
    Get the configured LLM instance for generation.
    Currently hardcoded to Groq natively, but provides an abstraction
    point for easily swapping to Anthropic, OpenAI, or local Ollama models
    in the future (similar to the reference architecture).
    """
    return Groq(
        model="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY,
        temperature=0.7,
    )
