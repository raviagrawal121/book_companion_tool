"""
OpenAI Client
=============
Provides a single cached OpenAI client instance and
the LangChain LLM instances used across the application.

All model config comes from settings.py and config.py —
nothing is hardcoded here.

Usage:
    from app.ai.openai_client import get_chat_llm, get_topic_llm
    llm = get_chat_llm()
"""

from functools import lru_cache
from langchain_openai import ChatOpenAI
from openai import OpenAI

from app.core.settings import settings
from app.core.config import LLMConfig


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Raw OpenAI client — used for direct API calls if needed."""
    return OpenAI(api_key=settings.openai_api_key)


@lru_cache(maxsize=1)
def get_chat_llm() -> ChatOpenAI:
    """
    LangChain ChatOpenAI for main Max responses.
    Higher temperature for conversational, friendly tone.
    """
    return ChatOpenAI(
        model=settings.chat_model,
        temperature=LLMConfig.TEMPERATURE,
        max_tokens=LLMConfig.MAX_TOKENS,
        openai_api_key=settings.openai_api_key,
    )


@lru_cache(maxsize=1)
def get_topic_llm() -> ChatOpenAI:
    """
    LangChain ChatOpenAI for topic classification.
    Zero temperature for deterministic, consistent topic tags.
    """
    return ChatOpenAI(
        model=settings.chat_model,
        temperature=LLMConfig.TOPIC_TEMPERATURE,
        max_tokens=LLMConfig.TOPIC_MAX_TOKENS,
        openai_api_key=settings.openai_api_key,
    )