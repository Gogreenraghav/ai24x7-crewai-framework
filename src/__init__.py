"""
CrewAI Multi-Agent Framework
A production-ready multi-agent system using CrewAI + DeepSeek API
"""

__version__ = "1.0.0"

from .core import CrewManager, get_crew_manager
from .agents import (
    get_agent,
    get_agent_metadata,
    list_available_agents,
    AGENT_REGISTRY
)
from .llm import create_deepseek_llm, create_reasoning_llm, create_coding_llm
from .memory import PersistentMemory, get_memory

__all__ = [
    "CrewManager",
    "get_crew_manager",
    "get_agent",
    "get_agent_metadata",
    "list_available_agents",
    "AGENT_REGISTRY",
    "create_deepseek_llm",
    "create_reasoning_llm",
    "create_coding_llm",
    "PersistentMemory",
    "get_memory",
]
