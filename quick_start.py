#!/usr/bin/env python
"""
Quick Start Script for CrewAI Multi-Agent Framework
Run this to verify installation and create your first crew
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...\n")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 11):
        issues.append(f"❌ Python 3.11+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
    else:
        print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        issues.append("❌ DEEPSEEK_API_KEY not set in .env file")
    elif api_key == "your_deepseek_api_key_here":
        issues.append("❌ Please replace placeholder API key in .env file")
    else:
        print(f"✅ DeepSeek API key configured ({api_key[:10]}...)")
    
    # Check if packages are installed
    try:
        import crewai
        print(f"✅ CrewAI installed (version {crewai.__version__ if hasattr(crewai, '__version__') else 'unknown'})")
    except ImportError:
        issues.append("❌ CrewAI not installed - run: pip install -r requirements.txt")
    
    try:
        import chromadb
        print(f"✅ ChromaDB installed")
    except ImportError:
        issues.append("❌ ChromaDB not installed - run: pip install -r requirements.txt")
    
    try:
        import requests
        print(f"✅ Requests installed")
    except ImportError:
        issues.append("❌ Requests not installed - run: pip install -r requirements.txt")
    
    print()
    
    if issues:
        print("⚠️  Issues found:\n")
        for issue in issues:
            print(f"  {issue}")
        print("\n❌ Please fix the issues above before continuing.\n")
        return False
    
    print("✅ All checks passed! Environment is ready.\n")
    return True


def demo_crew():
    """Create and show a demo crew"""
    print("="*60)
    print("🚀 Creating Demo Crew")
    print("="*60 + "\n")
    
    try:
        from src import get_crew_manager
        
        manager = get_crew_manager()
        
        print("📋 Creating a simple 3-agent crew for a blog platform...\n")
        
        crew = manager.create_crew(
            project_name="Blog Platform Demo",
            agent_types=["architect", "backend", "frontend"],
            tasks=[
                {
                    "description": """Design database schema for a blog platform.
                    
                    Requirements:
                    - User accounts with profiles
                    - Blog posts with categories and tags
                    - Comments with threading support
                    - Like/reaction system
                    
                    Deliverables:
                    - Database schema design
                    - ER diagram description
                    - Index recommendations
                    """,
                    "expected_output": "Complete database schema documentation",
                    "agent_index": 0
                },
                {
                    "description": """Design REST API for the blog platform.
                    
                    Requirements:
                    - Authentication endpoints
                    - Post CRUD operations
                    - Comment management
                    - Search and filtering
                    
                    Deliverables:
                    - API endpoint specification
                    - Request/response examples
                    - Authentication flow
                    """,
                    "expected_output": "Complete API documentation",
                    "agent_index": 1
                },
                {
                    "description": """Design React UI components for the blog.
                    
                    Requirements:
                    - Home page with post feed
                    - Post detail page with comments
                    - User profile page
                    - Post editor interface
                    
                    Deliverables:
                    - Component structure
                    - State management approach
                    - Responsive design strategy
                    """,
                    "expected_output": "UI component architecture",
                    "agent_index": 2
                }
            ]
        )
        
        print("✅ Crew created successfully!\n")
        print(f"👥 Agents in crew: {len(crew.agents)}")
        for i, agent in enumerate(crew.agents, 1):
            print(f"  {i}. {agent.role}")
        
        print(f"\n📋 Tasks to execute: {len(crew.tasks)}")
        for i, task in enumerate(crew.tasks, 1):
            print(f"  {i}. {task.description.split('.')[0]}...")
        
        print("\n💡 To execute this crew, run:")
        print("   result = manager.execute_crew(crew)")
        print("\n⚠️  Note: Execution will make API calls to DeepSeek\n")
        
        # Show available agents
        print("="*60)
        print("🤖 Available Agents")
        print("="*60 + "\n")
        
        agents = manager.list_agents()
        for agent in agents:
            print(f"• {agent['name']} ({agent['type']})")
            print(f"  {agent['specialization']}")
        
        print("\n" + "="*60)
        print("✅ Quick Start Complete!")
        print("="*60)
        print("\n📚 Next steps:")
        print("  1. Review example_usage.py for more examples")
        print("  2. Check README.md for comprehensive documentation")
        print("  3. Explore src/agents/ to see agent implementations")
        print("  4. Try executing a crew with: manager.execute_crew(crew)")
        print()
        
    except Exception as e:
        print(f"❌ Error creating demo crew: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    print("\n" + "🎯 "*20)
    print("CrewAI Multi-Agent Framework - Quick Start")
    print("🎯 "*20 + "\n")
    
    if not check_environment():
        sys.exit(1)
    
    demo_crew()


if __name__ == "__main__":
    main()
