"""
CrewAI Multi-Agent Framework
A production-ready multi-agent system using CrewAI + DeepSeek API
"""

__version__ = "1.0.0"

# Lazy imports to avoid requiring all dependencies upfront
# Import specific modules as needed to avoid circular dependencies

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
