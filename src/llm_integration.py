import os
from openai import AsyncOpenAI
from typing import List, Dict, Optional
import httpx

class LLMIntegration:
    """
    Handles integration with various LLM providers
    """
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_queries(self, prompt: str, n: int = 3) -> List[str]:
        """
        Generate search queries from LLM
        Args:
            prompt: The research prompt
            n: Number of queries to generate
        Returns:
            List of search queries
        """
        response = await self.client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4-turbo"),
            messages=[
                {"role": "system", "content": "You are a research assistant that generates effective web search queries."},
                {"role": "user", "content": f"Generate {n} distinct search queries for: {prompt}"}
            ],
            temperature=0.7,
            n=n
        )
        
        return [choice.message.content for choice in response.choices]
    
    async def analyze_results(self, content: str, query: str) -> Dict:
        """
        Analyze search results with LLM
        Args:
            content: Extracted content to analyze
            query: Original research query
        Returns:
            Dictionary with analysis results
        """
        response = await self.client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4-turbo"),
            messages=[
                {"role": "system", "content": "You are a research analyst. Extract key insights and suggest follow-up questions."},
                {"role": "user", "content": f"Research query: {query}\n\nContent:\n{content}\n\nExtract key insights and suggest follow-up questions."}
            ],
            temperature=0.5
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "follow_ups": self._extract_follow_ups(response.choices[0].message.content)
        }
    
    def _extract_follow_ups(self, analysis: str) -> List[str]:
        """Helper to extract follow-up questions from analysis"""
        # Simple extraction - can be enhanced
        lines = analysis.split("\n")
        return [line[2:].strip() for line in lines if line.startswith("-") or line.startswith("*")]