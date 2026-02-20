from abc import ABC, abstractmethod
from typing import List, Dict
import requests


class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: List[dict]) -> str:
        pass

    @abstractmethod
    def supports_vision(self) -> bool:
        pass


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = 'gpt-4o'):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def chat(self, messages: List[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    def supports_vision(self) -> bool:
        return True


class OllamaClient(LLMClient):
    def __init__(self, base_url: str = 'http://localhost:11434'):
        self.base_url = base_url

    def chat(self, messages: List[dict]) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": "llama2",
            "messages": messages,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]

    def supports_vision(self) -> bool:
        return False


class MissingAPIKeyError(Exception):
    pass


def get_llm_client() -> LLMClient:
    from .config import get_provider, get_api_key, get_model, get_ollama_base_url
    
    provider = get_provider()
    
    if provider == 'openai':
        api_key = get_api_key('openai')
        if not api_key:
            raise MissingAPIKeyError("OpenAI API key is not set. Please configure it in the MoleculeChat settings.")
        model = get_model()
        return OpenAIClient(api_key=api_key, model=model)
    elif provider == 'ollama':
        base_url = get_ollama_base_url()
        return OllamaClient(base_url=base_url)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
