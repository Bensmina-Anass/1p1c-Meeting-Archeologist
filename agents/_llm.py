import os
from crewai import LLM


def local_llm(max_tokens: int = 2048) -> LLM:
    return LLM(
        model="openai/qwen2.5",
        base_url=os.getenv("OPENAI_API_BASE", "http://localhost:8080/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "dummy"),
        max_tokens=max_tokens,
    )
