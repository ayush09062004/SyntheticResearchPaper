"""
groq_client.py
Handles Groq API connections with round-robin key rotation and retry logic.
"""

import time
import random
from groq import Groq


class GroqClientManager:
    """Manages multiple Groq API keys with round-robin rotation and retry."""

    def __init__(self, api_keys: list[str]):
        if not api_keys:
            raise ValueError("At least one Groq API key is required.")
        self.api_keys = [k.strip() for k in api_keys if k.strip()]
        self.current_index = 0
        self.clients = [Groq(api_key=key) for key in self.api_keys]

    def _next_client(self) -> tuple[Groq, str]:
        """Return next client in round-robin order."""
        client = self.clients[self.current_index]
        key = self.api_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client, key

    def complete(
        self,
        messages: list[dict],
        model: str = "openai/gpt-oss-120b",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> str:
        """
        Call Groq API with automatic key rotation and retry on failure.
        Returns the text content of the response.
        """
        last_error = None

        for attempt in range(max_retries * len(self.clients)):
            client, key_hint = self._next_client()
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                err_str = str(e).lower()

                # Rate limit → wait and rotate
                if "rate_limit" in err_str or "429" in err_str:
                    wait = 2 ** (attempt % 4) + random.uniform(0, 1)
                    time.sleep(wait)
                    continue

                # Auth error → skip this key permanently
                if "auth" in err_str or "401" in err_str:
                    print(f"[GroqClient] Auth error on key ending ...{key_hint[-4:]}. Skipping.")
                    if len(self.clients) > 1:
                        idx = self.api_keys.index(key_hint) if key_hint in self.api_keys else -1
                        if idx >= 0:
                            self.clients.pop(idx)
                            self.api_keys.pop(idx)
                            self.current_index = self.current_index % len(self.clients)
                    continue

                # Other errors → short wait and retry
                time.sleep(1)

        raise RuntimeError(f"All Groq API attempts failed. Last error: {last_error}")
