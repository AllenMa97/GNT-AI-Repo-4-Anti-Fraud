"""
LLM API Client — DeepSeek Integration
─────────────────────────────────────
All PII filtering happens BEFORE this module is called.
This module only sends already-filtered text to the API.
"""

import time
import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

from .config import get_api_config, APIConfig

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Thin wrapper around DeepSeek API for SOP-DAG experiments."""

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or get_api_config()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        self._total_tokens: int = 0
        self._total_calls: int = 0

    # ── Public API ──────────────────────────────────────────────────────────

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send a prompt to DeepSeek and return the response text.

        Args:
            system_prompt: System-level instruction
            user_prompt: Task-specific prompt (data already filtered)
            model: Model name (default: config.model_fast)
            temperature: Sampling temperature (default: config.temperature)
            response_format: Optional JSON schema for structured output

        Returns:
            Raw response text from the model
        """
        model = model or self.config.model_fast
        temperature = (
            temperature if temperature is not None else self.config.temperature
        )

        for attempt in range(self.config.max_retries):
            try:
                kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": self.config.max_tokens,
                }

                if response_format:
                    kwargs["response_format"] = response_format

                response = self.client.chat.completions.create(**kwargs)

                usage = response.usage
                if usage:
                    self._total_tokens += usage.total_tokens

                self._total_calls += 1

                return response.choices[0].message.content or ""

            except Exception as e:
                logger.warning(
                    f"API call attempt {attempt + 1}/{self.config.max_retries} "
                    f"failed: {e}"
                )
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise RuntimeError(
                        f"DeepSeek API call failed after "
                        f"{self.config.max_retries} attempts: {e}"
                    ) from e

        return ""

    def call_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Call DeepSeek and parse the response as JSON.

        Returns None if parsing fails.
        """
        raw = self.call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
        )

        # Extract JSON from response (strip markdown fences if present)
        text = raw.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from response: {text[:200]}...")
            return None

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    @property
    def total_calls(self) -> int:
        return self._total_calls

    def reset_stats(self):
        self._total_tokens = 0
        self._total_calls = 0
