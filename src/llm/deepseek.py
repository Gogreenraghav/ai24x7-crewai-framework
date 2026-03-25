"""
DeepSeek LLM Integration for CrewAI
Provides custom LLM class for CrewAI agents using DeepSeek API
"""

import os
import requests
from typing import Any, Dict, List, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field


class DeepSeekLLM(LLM):
    """Custom DeepSeek LLM wrapper for CrewAI agents"""
    
    api_key: str = Field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    api_base: str = Field(default_factory=lambda: os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"))
    model: str = Field(default="deepseek-chat")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call DeepSeek API with the given prompt"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API error: {str(e)}")
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return identifying parameters for caching"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


def create_deepseek_llm(model: str = "deepseek-chat", temperature: float = 0.7) -> DeepSeekLLM:
    """
    Factory function to create DeepSeek LLM instances
    
    Args:
        model: Model name (deepseek-chat or deepseek-coder)
        temperature: Temperature for response generation
        
    Returns:
        Configured DeepSeekLLM instance
    """
    return DeepSeekLLM(model=model, temperature=temperature)


def create_reasoning_llm() -> DeepSeekLLM:
    """Create LLM for reasoning tasks"""
    model = os.getenv("DEEPSEEK_REASONING_MODEL", "deepseek-chat")
    return create_deepseek_llm(model=model, temperature=0.7)


def create_coding_llm() -> DeepSeekLLM:
    """Create LLM for coding tasks"""
    model = os.getenv("DEEPSEEK_CODING_MODEL", "deepseek-coder")
    return create_deepseek_llm(model=model, temperature=0.3)
