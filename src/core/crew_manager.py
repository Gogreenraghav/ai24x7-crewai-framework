"""
Crew Manager - Main orchestrator for CrewAI multi-agent system
Manages crew creation, task assignment, and project execution
"""

import os
from typing import List, Dict, Any, Optional
from crewai import Crew, Task, Process
from src.agents import (
    get_agent,
    get_agent_metadata,
    list_available_agents,
    AGENT_REGISTRY
)
from src.memory import get_memory
import json
from datetime import datetime


class CrewManager:
    """
    Main orchestrator for managing CrewAI agents and crews
    """
    
    def __init__(self):
        """Initialize Crew Manager"""
        self.memory = get_memory()
        self.active_crews: Dict[str, Crew] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def create_crew(
        self,
        project_name: str,
        agent_types: List[str],
        tasks: List[Dict[str, Any]],
        process: Process = Process.sequential,
        verbose: bool = True
    ) -> Crew:
        """
        Create a new crew for a project
        
        Args:
            project_name: Name of the project
            agent_types: List of agent types to include
            tasks: List of task definitions
            process: Crew process type (sequential or hierarchical)
            verbose: Enable verbose logging
            
        Returns:
            Configured Crew instance
        """
        # Validate agent types
        available_agents = list_available_agents()
        for agent_type in agent_types:
            if agent_type not in available_agents:
                raise ValueError(f"Invalid agent type: {agent_type}. Available: {available_agents}")
        
        # Create agents
        agents = [get_agent(agent_type) for agent_type in agent_types]
        
        # Create tasks
        crew_tasks = []
        for i, task_def in enumerate(tasks):
            # Determine which agent to assign the task to
            agent_idx = task_def.get("agent_index", i % len(agents))
            agent = agents[agent_idx]
            
            task = Task(
                description=task_def["description"],
                expected_output=task_def.get("expected_output", "Completed task deliverables"),
                agent=agent
            )
            crew_tasks.append(task)
        
        # Create crew
        crew = Crew(
            agents=agents,
            tasks=crew_tasks,
            process=process,
            verbose=verbose,
            memory=True
        )
        
        # Store crew
        crew_id = f"{project_name}_{datetime.now().timestamp()}"
        self.active_crews[crew_id] = crew
        
        # Store in memory
        self.memory.store_memory(
            agent_id="crew_manager",
            content=f"Created crew for project: {project_name}",
            metadata={
                "project_name": project_name,
                "crew_id": crew_id,
                "agent_types": agent_types,
                "num_tasks": len(tasks),
                "process": str(process)
            }
        )
        
        return crew
    
    def create_full_stack_crew(
        self,
        project_name: str,
        project_description: str,
        include_all_agents: bool = True,
        custom_agent_types: Optional[List[str]] = None
    ) -> Crew:
        """
        Create a comprehensive full-stack development crew
        
        Args:
            project_name: Name of the project
            project_description: Detailed project description
            include_all_agents: Include all available agents
            custom_agent_types: Custom list of agent types to include
            
        Returns:
            Configured Crew instance
        """
        # Determine which agents to include
        if custom_agent_types:
            agent_types = custom_agent_types
        elif include_all_agents:
            agent_types = ["architect", "backend", "frontend", "qa", "devops", "pm"]
        else:
            # Default essential agents
            agent_types = ["architect", "backend", "frontend", "qa"]
        
        # Define standard tasks for full-stack development
        tasks = [
            {
                "description": f"""Analyze the project requirements and design the database schema.
                
                Project: {project_name}
                Description: {project_description}
                
                Deliverables:
                - Complete database schema with tables, relationships, and constraints
                - ER diagram or schema documentation
                - Index recommendations for query optimization
                - Migration strategy
                - Data validation rules
                """,
                "expected_output": "Complete database schema documentation with ER diagrams and migration plan",
                "agent_index": agent_types.index("architect") if "architect" in agent_types else 0
            },
            {
                "description": f"""Design and implement the backend API based on the database schema.
                
                Project: {project_name}
                Description: {project_description}
                
                Deliverables:
                - RESTful API endpoints or GraphQL schema
                - Authentication and authorization implementation
                - Business logic and data validation
                - API documentation (OpenAPI/Swagger)
                - Error handling and logging
                """,
                "expected_output": "Complete backend API implementation with documentation",
                "agent_index": agent_types.index("backend") if "backend" in agent_types else 0
            },
            {
                "description": f"""Build the frontend user interface that consumes the backend API.
                
                Project: {project_name}
                Description: {project_description}
                
                Deliverables:
                - Responsive UI components
                - State management implementation
                - API integration with error handling
                - User authentication flows
                - Accessibility compliance
                """,
                "expected_output": "Complete frontend application with responsive UI and API integration",
                "agent_index": agent_types.index("frontend") if "frontend" in agent_types else 0
            },
            {
                "description": f"""Create comprehensive test suites for the application.
                
                Project: {project_name}
                Description: {project_description}
                
                Deliverables:
                - Unit tests for backend and frontend
                - Integration tests for API endpoints
                - E2E tests for critical user flows
                - Test coverage report (target 80%+)
                - Bug reports and quality assessment
                """,
                "expected_output": "Complete test suite with coverage report and quality assessment",
                "agent_index": agent_types.index("qa") if "qa" in agent_types else 0
            }
        ]
        
        # Add DevOps tasks if included
        if "devops" in agent_types:
            tasks.append({
                "description": f"""Set up CI/CD pipeline and deployment infrastructure.
                
                Project: {project_name}
                Description: {project_description}
                
                Deliverables:
                - CI/CD pipeline configuration (GitHub Actions or similar)
                - Docker containerization
                - Kubernetes manifests or deployment scripts
                - Monitoring and alerting setup
                - Deployment documentation
                """,
                "expected_output": "Complete CI/CD pipeline and deployment infrastructure",
                "agent_index": agent_types.index("devops")
            })
        
        # Add PM tasks if included
        if "pm" in agent_types:
            tasks.append({
                "description": f"""Create product launch strategy and marketing plan.
                
                Project: {project_name}
                Description: {project_description}
                
                Deliverables:
                - App store optimization (ASO) strategy
                - Marketing campaign plan
                - User acquisition funnel design
                - Analytics tracking plan
                - Launch checklist and timeline
                """,
                "expected_output": "Complete product launch and marketing strategy",
                "agent_index": agent_types.index("pm")
            })
        
        return self.create_crew(
            project_name=project_name,
            agent_types=agent_types,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def execute_crew(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a crew and return results
        
        Args:
            crew: Crew instance to execute
            inputs: Optional input parameters for the crew
            
        Returns:
            Execution results
        """
        start_time = datetime.now()
        
        try:
            # Execute crew
            result = crew.kickoff(inputs=inputs or {})
            
            # Record execution
            execution_record = {
                "timestamp": start_time.isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "status": "success",
                "result": str(result)
            }
            
            self.execution_history.append(execution_record)
            
            # Store in memory
            self.memory.store_memory(
                agent_id="crew_manager",
                content=f"Crew execution completed successfully",
                metadata=execution_record
            )
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_record["duration_seconds"]
            }
            
        except Exception as e:
            # Record failure
            execution_record = {
                "timestamp": start_time.isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "status": "failed",
                "error": str(e)
            }
            
            self.execution_history.append(execution_record)
            
            # Store in memory
            self.memory.store_memory(
                agent_id="crew_manager",
                content=f"Crew execution failed: {str(e)}",
                metadata=execution_record
            )
            
            return {
                "status": "failed",
                "error": str(e),
                "execution_time": execution_record["duration_seconds"]
            }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent execution history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        return self.execution_history[-limit:]
    
    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        """
        Get information about a specific agent type
        
        Args:
            agent_type: Agent type identifier
            
        Returns:
            Agent metadata
        """
        return get_agent_metadata(agent_type)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all available agents with metadata
        
        Returns:
            List of agent metadata
        """
        agents = []
        for agent_type in list_available_agents():
            metadata = get_agent_metadata(agent_type)
            agents.append({
                "type": agent_type,
                **metadata
            })
        return agents


# Global crew manager instance
_crew_manager_instance: Optional[CrewManager] = None


def get_crew_manager() -> CrewManager:
    """Get or create global crew manager instance"""
    global _crew_manager_instance
    if _crew_manager_instance is None:
        _crew_manager_instance = CrewManager()
    return _crew_manager_instance
