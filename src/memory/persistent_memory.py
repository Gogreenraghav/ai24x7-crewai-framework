"""
Persistent Memory Management using ChromaDB
Provides long-term memory storage and retrieval for CrewAI agents
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
import json


class PersistentMemory:
    """ChromaDB-backed persistent memory for agents"""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize persistent memory storage
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIRECTORY", 
            "./chroma_db"
        )
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME",
            "crewai_memory"
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "CrewAI agent memory storage"}
        )
    
    def store_memory(
        self,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Store a memory entry
        
        Args:
            agent_id: Identifier for the agent
            content: Memory content to store
            metadata: Additional metadata
            memory_id: Optional custom memory ID
            
        Returns:
            Memory ID
        """
        if memory_id is None:
            memory_id = f"{agent_id}_{datetime.now().timestamp()}"
        
        # Prepare metadata
        mem_metadata = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # Store in ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=[mem_metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    def retrieve_memories(
        self,
        agent_id: str,
        query: Optional[str] = None,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories
        
        Args:
            agent_id: Identifier for the agent
            query: Search query (semantic search if provided)
            n_results: Number of results to return
            where: Additional metadata filters
            
        Returns:
            List of memory entries
        """
        # Build where clause
        where_clause = {"agent_id": agent_id}
        if where:
            where_clause.update(where)
        
        # Retrieve from ChromaDB
        if query:
            # Semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
        else:
            # Get all matching metadata
            results = self.collection.get(
                where=where_clause,
                limit=n_results
            )
        
        # Format results
        memories = []
        if query:
            # Query results format
            for i in range(len(results["ids"][0])):
                memories.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
        else:
            # Get results format
            for i in range(len(results["ids"])):
                memories.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
        
        return memories
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a specific memory
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            Success status
        """
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False
    
    def clear_agent_memories(self, agent_id: str) -> int:
        """
        Clear all memories for a specific agent
        
        Args:
            agent_id: Identifier for the agent
            
        Returns:
            Number of memories deleted
        """
        # Get all memories for agent
        memories = self.collection.get(where={"agent_id": agent_id})
        
        if memories["ids"]:
            self.collection.delete(ids=memories["ids"])
            return len(memories["ids"])
        
        return 0
    
    def get_memory_stats(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Args:
            agent_id: Optional agent ID to filter stats
            
        Returns:
            Dictionary with memory statistics
        """
        if agent_id:
            memories = self.collection.get(where={"agent_id": agent_id})
            return {
                "agent_id": agent_id,
                "total_memories": len(memories["ids"]),
                "collection_name": self.collection_name
            }
        else:
            count = self.collection.count()
            return {
                "total_memories": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }


# Global memory instance
_memory_instance: Optional[PersistentMemory] = None


def get_memory() -> PersistentMemory:
    """Get or create global memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = PersistentMemory()
    return _memory_instance
