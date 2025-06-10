import pytest
from fastapi.testclient import TestClient
from src.main import app, SearchRequest

client = TestClient(app)

def test_search_endpoint():
    """Test the search endpoint with mock data"""
    test_request = {
        "query": "test query",
        "depth": 1,
        "breadth": 2
    }
    
    response = client.post("/search", json=test_request)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "sources" in data
    assert "follow_ups" in data

@pytest.mark.asyncio
async def test_search_logic():
    """Test the search processing logic with mocks"""
    from src.main import process_search
    from unittest.mock import AsyncMock
    
    # Create mock LLM and MCP integrations
    mock_llm = AsyncMock()
    mock_llm.generate_queries.return_value = ["query 1", "query 2"]
    mock_llm.analyze_results.return_value = {
        "analysis": "test analysis",
        "follow_ups": ["follow up 1"]
    }
    
    mock_mcp = AsyncMock()
    mock_mcp.web_search.return_value = {
        "content": "test content",
        "metadata": {},
        "sources": [{"url": "http://test.com"}]
    }
    mock_mcp.extract_content.return_value = {
        "content": "extracted content",
        "metadata": {},
        "sources": [{"url": "http://test.com"}]
    }
    
    # Test the search process
    result = await process_search(
        query="test query",
        depth=1,
        breadth=2,
        llm=mock_llm,
        mcp=mock_mcp
    )
    
    assert result.content == "test analysis"
    assert len(result.sources) > 0
    assert len(result.follow_ups) > 0