import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        api_key = api_key or settings.OPENROUTER_API_KEY
        base_url = base_url or settings.OPENROUTER_BASE_URL
        
        if not api_key:
            logger.warning("OPENROUTER_API_KEY is not set!")
            
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": settings.HOST,
                "X-Title": settings.APP_NAME,
            }
        )

    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", settings.OPENROUTER_DEFAULT_MODEL),
                messages=messages,
                **{k: v for k, v in kwargs.items() if k != "model"}
            )
            # Convert back to the dictionary format expected by the rest of the app
            return response.model_dump()
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise
