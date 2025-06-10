import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
from llm_integration import LLMIntegration
from mcp_integration import MCPIntegration, MCPToolResponse

app = FastAPI(title="DeepSearch MCP LLM API")

class SearchRequest(BaseModel):
    query: str
    depth: Optional[int] = 1
    breadth: Optional[int] = 3
    llm_provider: Optional[str] = "openai"
    mcp_tools: Optional[List[str]] = ["web_search", "content_extractor"]

class SearchResult(BaseModel):
    content: str
    sources: List[Dict]
    follow_ups: List[str]
    depth: int

@app.post("/search", response_model=SearchResult)
async def deep_search(request: SearchRequest):
    """
    Main endpoint for deep search requests
    """
    try:
        # Initialize components
        llm = LLMIntegration(provider=request.llm_provider)
        mcp = MCPIntegration(tools=request.mcp_tools)
        
        # Process request
        results = await process_search(
            query=request.query,
            depth=request.depth,
            breadth=request.breadth,
            llm=llm,
            mcp=mcp
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await mcp.close()

async def process_search(
    query: str, 
    depth: int, 
    breadth: int, 
    llm: LLMIntegration, 
    mcp: MCPIntegration
) -> SearchResult:
    """
    Core search processing logic with iterative deepening
    """
    all_content = []
    all_sources = []
    follow_ups = []
    
    # Generate initial queries
    queries = await llm.generate_queries(query, n=breadth)
    
    # Process initial search results
    search_tasks = [mcp.web_search(q) for q in queries]
    search_results = await asyncio.gather(*search_tasks)
    
    # Extract and analyze content
    for result in search_results:
        all_sources.extend(result.sources)
        
        # Get content from top results
        content_tasks = [mcp.extract_content(src["url"]) for src in result.sources[:3]]
        contents = await asyncio.gather(*content_tasks)
        
        for content in contents:
            all_content.append(content.content)
            analysis = await llm.analyze_results(content.content, query)
            follow_ups.extend(analysis["follow_ups"])
    
    # Process follow-up questions if depth > 1
    if depth > 1 and follow_ups:
        follow_up_results = await asyncio.gather(
            *[process_search(
                q, 
                depth-1, 
                breadth, 
                llm, 
                mcp
              ) for q in follow_ups[:breadth]]
        )
        
        for result in follow_up_results:
            all_content.append(result.content)
            all_sources.extend(result.sources)
            follow_ups.extend(result.follow_ups)
    
    # Generate final summary
    final_content = "\n\n".join(all_content)
    summary = await llm.analyze_results(final_content, query)
    
    return SearchResult(
        content=summary["analysis"],
        sources=all_sources,
        follow_ups=follow_ups,
        depth=depth
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)