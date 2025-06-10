# DeepSearch MCP LLM Integration

A script-controlled deep search system combining LLM API and MCP tools for comprehensive web research.

## Features

- **LLM-Powered Query Generation**: Uses OpenAI models to generate optimized search queries
- **MCP Tool Integration**: Leverages Model Context Protocol tools for web search and content extraction
- **Iterative Deep Search**: Performs multi-level research with configurable depth and breadth
- **API-First Design**: RESTful interface for easy integration with other systems
- **Extensible Architecture**: Supports multiple LLM providers and MCP tool configurations

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/spicytougan/deepsearch-mcp-llm.git
cd deepsearch-mcp-llm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Configure your API keys in `.env`:
```
OPENAI_API_KEY=your_api_key
MCP_API_KEY=your_mcp_key
```

5. Run the API server:
```bash
uvicorn src.main:app --reload
```

## API Usage

Send POST requests to `/search` with JSON payload:
```json
{
  "query": "latest developments in AI research",
  "depth": 2,
  "breadth": 3,
  "llm_provider": "openai",
  "mcp_tools": ["web_search", "content_extractor"]
}
```

## Development

### Project Structure

```
├── src/
│   ├── main.py            # Main API service
│   ├── llm_integration.py # LLM provider interfaces
│   └── mcp_integration.py # MCP tool handlers
├── tests/                 # Unit and integration tests
├── requirements.txt       # Python dependencies
└── .env.example           # Environment configuration template
```

### Testing

Run tests with:
```bash
pytest tests/
```

## License

MIT