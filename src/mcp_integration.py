import os
import httpx
from typing import Dict, List, Optional
from pydantic import BaseModel

class MCPToolResponse(BaseModel):
    content: str
    metadata: Dict
    sources: List[Dict]

class MCPIntegration:
    """
    Handles integration with MCP tools for web search and content extraction
    """
    def __init__(self, tools: List[str] = None):
        self.base_url = os.getenv("MCP_SERVER_URL", "https://api.mcp.example.com")
        self.api_key = os.getenv("MCP_API_KEY")
        self.tools = tools or ["web_search", "content_extractor"]
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def web_search(self, query: str, n_results: int = 5) -> MCPToolResponse:
        """
        Perform web search using MCP tools
        Args:
            query: Search query
            n_results: Number of results to return
        Returns:
            MCPToolResponse with search results
        """
        response = await self.client.post(
            "/tools/call",
            json={
                "tool": "web_search",
                "parameters": {
                    "query": query,
                    "num_results": n_results,
                    "time_range": "month"
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return MCPToolResponse(
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            sources=data.get("sources", [])
        )
    
    async def extract_content(self, url: str) -> MCPToolResponse:
        """
        Extract content from URL using MCP tools
        Args:
            url: URL to extract content from
        Returns:
            MCPToolResponse with extracted content
        """
        response = await self.client.post(
            "/tools/call",
            json={
                "tool": "content_extractor",
                "parameters": {
                    "url": url,
                    "extract_mode": "clean"
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return MCPToolResponse(
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            sources=[{"url": url}]
        )
    
    async def close(self):
        """Close HTTP client connections"""
        await self.client.aclose()
    
    def __del__(self):
        """Ensure connections are closed on destruction"""
        import asyncio
        try:
            asyncio.get_event_loop().run_until_complete(self.close())
        except:
            pass