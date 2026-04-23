
import httpx
from typing import List, Dict, Any
from app.core.config import settings
class OpenRouterClient:
    def __init__(self, api_key: str = settings.OPENROUTER_API_KEY, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": messages,
            **kwargs
        }
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
