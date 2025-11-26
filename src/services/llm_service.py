import httpx
import logging
import re
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config.settings import settings
from typing import List, Dict, Optional

logger = logging.getLogger("healthy_rag")

class LLMService:
    def __init__(self):
        # DeepSeek Config
        self.ds_api_key = settings.DEEP_SEEK_API_KEY
        self.ds_base_url = "https://api.deepseek.com"
        self.ds_timeout = settings.DEEP_SEEK_TIMEOUT
        self.ds_chat_model = "deepseek-chat"
        self.ds_reasoner_model = settings.DEEP_SEEK_MODEL_REASONER

        # Gemini Config
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_base_url = settings.GEMINI_BASE_URL
        self.gemini_model = settings.GEMINI_MODEL
        self.gemini_timeout = settings.GEMINI_TIMEOUT

        # Compatibility properties for existing code
        self.default_model = "deepseek-chat"  # Used as fallback/identifier
        self.reasoner_model = settings.DEEP_SEEK_MODEL_REASONER

    @retry(
        stop=stop_after_attempt(2), # Try Gemini twice before failing over
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        thinking_level: str = "low",
        temperature: float = 1.0
    ) -> str:
        if not self.gemini_api_key:
            raise ValueError("Gemini API Key not configured")

        url = f"{self.gemini_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.gemini_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.gemini_model,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": temperature,
            "extra_body": {
                "thinking_level": thinking_level
            }
        }

        async with httpx.AsyncClient(timeout=self.gemini_timeout) as client:
            logger.info(f"Calling Gemini API ({thinking_level} thinking)...")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Strip <think> tags if present
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            
            return content

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def _call_deepseek(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None
    ) -> str:
        if not self.ds_api_key:
            raise ValueError("DeepSeek API Key not configured")

        url = f"{self.ds_base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.ds_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 4000,
            "stream": False
        }
        
        if temperature is not None:
            payload["temperature"] = temperature

        async with httpx.AsyncClient(timeout=self.ds_timeout) as client:
            logger.info(f"Calling DeepSeek API ({model})...")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        model: str = None, # Keeps compatibility, used to determine intent if thinking_level not explicit
        thinking_level: str = "low" # "low" for chat, "high" for report
    ) -> str:
        """
        Unified Chat Completion
        Prioritizes Gemini (with thinking_level).
        Falls back to DeepSeek if Gemini fails.
        """
        
        # Construct messages
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)

        # Determine config based on usage context
        # If model was passed as 'deepseek-reasoner', it implies high reasoning (Report)
        # If model was passed as 'deepseek-chat' or None, it implies low reasoning (Chat)
        
        effective_thinking_level = thinking_level
        
        # Try Gemini First
        try:
            return await self._call_gemini(
                messages=final_messages,
                thinking_level=effective_thinking_level
            )
        except Exception as e:
            logger.error(f"Gemini API failed: {str(e)}. Falling back to DeepSeek.")
            
            # Fallback Logic
            fallback_model = self.ds_chat_model
            fallback_temp = 0.7
            
            if effective_thinking_level == "high":
                fallback_model = self.ds_reasoner_model
                fallback_temp = None # Reasoner doesn't support temperature
            
            return await self._call_deepseek(
                messages=final_messages,
                model=fallback_model,
                temperature=fallback_temp
            )

llm_service = LLMService()
