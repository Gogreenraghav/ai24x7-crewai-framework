"""
Agent definitions for CrewAI multi-agent system
"""

from .architect_agent import create_architect_agent, AGENT_METADATA as architect_metadata
from .frontend_agent import create_frontend_agent, AGENT_METADATA as frontend_metadata
from .backend_agent import create_backend_agent, AGENT_METADATA as backend_metadata
from .qa_agent import create_qa_agent, AGENT_METADATA as qa_metadata
from .devops_agent import create_devops_agent, AGENT_METADATA as devops_metadata
from .pm_agent import create_pm_agent, AGENT_METADATA as pm_metadata


# Agent factory registry
AGENT_REGISTRY = {
    "architect": create_architect_agent,
    "frontend": create_frontend_agent,
    "backend": create_backend_agent,
    "qa": create_qa_agent,
    "devops": create_devops_agent,
    "pm": create_pm_agent,
}


# Agent metadata registry
METADATA_REGISTRY = {
    "architect": architect_metadata,
    "frontend": frontend_metadata,
    "backend": backend_metadata,
    "qa": qa_metadata,
    "devops": devops_metadata,
    "pm": pm_metadata,
}


def get_agent(agent_type: str):
    """
    Get agent by type
    
    Args:
        agent_type: Type of agent to create
        
    Returns:
        Agent instance
    """
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return AGENT_REGISTRY[agent_type]()


def get_agent_metadata(agent_type: str):
    """
    Get agent metadata by type
    
    Args:
        agent_type: Type of agent
        
    Returns:
        Agent metadata dictionary
    """
    if agent_type not in METADATA_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return METADATA_REGISTRY[agent_type]


def list_available_agents():
    """
    List all available agent types
    
    Returns:
        List of agent type names
    """
    return list(AGENT_REGISTRY.keys())


__all__ = [
    "create_architect_agent",
    "create_frontend_agent",
    "create_backend_agent",
    "create_qa_agent",
    "create_devops_agent",
    "create_pm_agent",
    "get_agent",
    "get_agent_metadata",
    "list_available_agents",
    "AGENT_REGISTRY",
    "METADATA_REGISTRY",
]
