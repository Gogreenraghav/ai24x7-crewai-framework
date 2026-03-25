#!/usr/bin/env python
"""
Example Usage of CrewAI Multi-Agent Framework
Demonstrates different ways to use the framework
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src import get_crew_manager, get_agent, list_available_agents
from src.memory import get_memory


def example_1_full_stack_crew():
    """Example 1: Create a full-stack development crew"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Full-Stack Development Crew")
    print("="*60 + "\n")
    
    manager = get_crew_manager()
    
    crew = manager.create_full_stack_crew(
        project_name="TaskManager App",
        project_description="""
        Build a modern task management application with:
        - User authentication (email/password + OAuth)
        - CRUD operations for tasks with categories and tags
        - Real-time collaboration features
        - Mobile apps (Flutter) + Web interface (React)
        - RESTful API with PostgreSQL backend
        - Push notifications for task updates
        """
    )
    
    print(f"✅ Created crew with {len(crew.agents)} agents")
    print(f"📋 Tasks to execute: {len(crew.tasks)}")
    
    # Uncomment to execute (will make API calls)
    # result = manager.execute_crew(crew)
    # print(f"Result: {result}")


def example_2_custom_crew():
    """Example 2: Create a custom crew with specific agents"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Crew (API Redesign)")
    print("="*60 + "\n")
    
    manager = get_crew_manager()
    
    crew = manager.create_crew(
        project_name="API Redesign",
        agent_types=["architect", "backend", "qa"],
        tasks=[
            {
                "description": "Design new database schema for multi-tenancy support",
                "expected_output": "Schema documentation with migration plan",
                "agent_index": 0  # Architect
            },
            {
                "description": "Implement GraphQL API with tenant isolation",
                "expected_output": "GraphQL schema and resolvers",
                "agent_index": 1  # Backend
            },
            {
                "description": "Create integration tests for tenant data isolation",
                "expected_output": "Test suite with 90%+ coverage",
                "agent_index": 2  # QA
            }
        ]
    )
    
    print(f"✅ Created custom crew with {len(crew.agents)} agents")
    print(f"📋 Tasks: {len(crew.tasks)}")


def example_3_list_agents():
    """Example 3: List all available agents"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Available Agents")
    print("="*60 + "\n")
    
    manager = get_crew_manager()
    agents = manager.list_agents()
    
    for agent in agents:
        print(f"\n🤖 {agent['name']} ({agent['type']})")
        print(f"   Specialization: {agent['specialization']}")
        print(f"   Primary Tasks:")
        for task in agent['primary_tasks']:
            print(f"     • {task}")


def example_4_memory_system():
    """Example 4: Work with persistent memory"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Persistent Memory System")
    print("="*60 + "\n")
    
    memory = get_memory()
    
    # Store some memories
    print("Storing memories...")
    memory.store_memory(
        agent_id="backend_agent",
        content="Implemented JWT authentication with refresh tokens",
        metadata={"project": "TaskManager", "feature": "auth"}
    )
    
    memory.store_memory(
        agent_id="backend_agent",
        content="Created RESTful API endpoints for task CRUD operations",
        metadata={"project": "TaskManager", "feature": "tasks"}
    )
    
    memory.store_memory(
        agent_id="frontend_agent",
        content="Built responsive React dashboard with Tailwind CSS",
        metadata={"project": "TaskManager", "feature": "ui"}
    )
    
    # Retrieve memories
    print("\nRetrieving backend agent memories...")
    memories = memory.retrieve_memories(
        agent_id="backend_agent",
        query="authentication",
        n_results=5
    )
    
    for mem in memories:
        print(f"  📝 {mem['content']}")
        print(f"     Metadata: {mem['metadata']}")
    
    # Get statistics
    stats = memory.get_memory_stats()
    print(f"\n📊 Memory Stats: {stats['total_memories']} total memories stored")


def example_5_individual_agent():
    """Example 5: Work with individual agents"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Individual Agent Usage")
    print("="*60 + "\n")
    
    from crewai import Crew, Task
    
    # Create specific agents
    backend_agent = get_agent("backend")
    qa_agent = get_agent("qa")
    
    print(f"✅ Created backend agent: {backend_agent.role}")
    print(f"✅ Created QA agent: {qa_agent.role}")
    
    # Create custom tasks
    tasks = [
        Task(
            description="Build REST API for user management with CRUD operations",
            agent=backend_agent,
            expected_output="Complete API implementation with documentation"
        ),
        Task(
            description="Create integration tests for user management API",
            agent=qa_agent,
            expected_output="Test suite with 85%+ coverage"
        )
    ]
    
    custom_crew = Crew(
        agents=[backend_agent, qa_agent],
        tasks=tasks,
        verbose=True
    )
    
    print(f"\n✅ Created custom crew with {len(custom_crew.agents)} agents")
    print(f"📋 Ready to execute {len(tasks)} tasks")


def example_6_marketing_crew():
    """Example 6: Marketing and product launch crew"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Product Launch Crew")
    print("="*60 + "\n")
    
    manager = get_crew_manager()
    
    crew = manager.create_crew(
        project_name="MobileFitness App Launch",
        agent_types=["pm", "frontend", "devops"],
        tasks=[
            {
                "description": """Create comprehensive ASO strategy for fitness app launch.
                
                App: MobileFitness - AI-powered workout planner
                Target: iOS and Android
                
                Deliverables:
                - App store title and description optimization
                - Keyword research and ranking strategy
                - Screenshot and preview video plan
                - Launch timeline and promotional strategy
                """,
                "expected_output": "Complete ASO and launch strategy document",
                "agent_index": 0  # PM
            },
            {
                "description": """Optimize app onboarding flow and UI for conversion.
                
                Focus areas:
                - First-time user experience
                - Permission requests timing
                - Feature discovery
                - Retention hooks
                """,
                "expected_output": "Optimized onboarding flow with wireframes",
                "agent_index": 1  # Frontend
            },
            {
                "description": """Set up analytics and monitoring for launch metrics.
                
                Requirements:
                - User acquisition tracking
                - Crash reporting
                - Performance monitoring
                - A/B testing infrastructure
                """,
                "expected_output": "Analytics and monitoring setup documentation",
                "agent_index": 2  # DevOps
            }
        ]
    )
    
    print(f"✅ Created product launch crew")
    print(f"📱 Focus: Mobile app marketing and optimization")
    print(f"👥 Agents: PM, Frontend, DevOps")


def main():
    """Run all examples"""
    print("\n" + "🚀 "*20)
    print("CrewAI Multi-Agent Framework - Example Usage")
    print("🚀 "*20)
    
    # Check if API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\n⚠️  WARNING: DEEPSEEK_API_KEY not set in .env file")
        print("Please add your API key to continue\n")
        return
    
    try:
        example_1_full_stack_crew()
        example_2_custom_crew()
        example_3_list_agents()
        example_4_memory_system()
        example_5_individual_agent()
        example_6_marketing_crew()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
        print("💡 Next Steps:")
        print("  1. Uncomment 'result = manager.execute_crew(crew)' to run crews")
        print("  2. Check ./chroma_db/ for persistent memory storage")
        print("  3. Customize agents and tasks for your projects")
        print("  4. Review README.md for advanced usage patterns\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
