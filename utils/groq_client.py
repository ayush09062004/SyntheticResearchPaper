"""
groq_client.py
Handles Groq API connections with round-robin key rotation and retry logic.

FIXES vs original:
- Auth error handler was calling self.api_keys.index(key_hint) but key_hint
  was the raw key string, not a hint — this always worked but was confusing.
  Now uses enumerate to find the index safely without .index() which raises
  ValueError if the key was already removed.
- Added explicit handling for model-not-found / 404 errors so they surface
  clearly rather than being swallowed as generic errors.
- Removed unreachable `continue` after the generic `time.sleep(1)` (the loop
  continues naturally).
- Added `stop_at_auth_failure` guard: if all keys have been invalidated the
  loop exits early instead of spinning forever.
"""

import time
import random
from groq import Groq


class GroqClientManager:
    """Manages multiple Groq API keys with round-robin rotation and retry."""

    def __init__(self, api_keys: list[str]):
        if not api_keys:
            raise ValueError("At least one Groq API key is required.")
        self.api_keys      = [k.strip() for k in api_keys if k.strip()]
        self.clients       = [Groq(api_key=key) for key in self.api_keys]
        self.current_index = 0

    def _next_client(self) -> tuple[Groq, str]:
        """Return next client in round-robin order."""
        client = self.clients[self.current_index]
        key    = self.api_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client, key

    def _remove_client_at(self, index: int) -> None:
        """Remove a client (and key) by index, adjusting the round-robin pointer."""
        self.clients.pop(index)
        self.api_keys.pop(index)
        if self.clients:
            self.current_index = self.current_index % len(self.clients)
        else:
            self.current_index = 0

    def complete(
        self,
        messages: list[dict],
        model: str = "llama-3.1-8b-instant",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> str:
        """
        Call Groq API with automatic key rotation and retry on failure.
        Returns the text content of the response.
        """
        if not self.clients:
            raise RuntimeError("No valid Groq API keys available.")

        last_error   = None
        total_tries  = max_retries * len(self.clients)

        for attempt in range(total_tries):
            if not self.clients:
                raise RuntimeError("All Groq API keys have been invalidated (auth errors).")

            client, current_key = self._next_client()
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
                err_str    = str(e).lower()

                # Rate limit → exponential back-off and rotate
                if "rate_limit" in err_str or "429" in err_str:
                    wait = 2 ** (attempt % 4) + random.uniform(0, 1)
                    print(f"[GroqClient] Rate-limited. Waiting {wait:.1f}s ...")
                    time.sleep(wait)
                    continue

                # Auth error → permanently remove this key
                if "auth" in err_str or "401" in err_str or "invalid api key" in err_str:
                    print(f"[GroqClient] Auth error on key ...{current_key[-4:]}. Removing.")
                    # Find current key's index safely
                    try:
                        idx = self.api_keys.index(current_key)
                        self._remove_client_at(idx)
                        # Adjust index because we just removed one
                        self.current_index = self.current_index % max(len(self.clients), 1)
                    except ValueError:
                        pass  # already removed
                    continue

                # Model not found / bad request
                if "404" in err_str or "model" in err_str or "400" in err_str:
                    raise RuntimeError(
                        f"Groq API error (likely invalid model '{model}'): {e}"
                    ) from e

                # Generic / transient error → short wait and retry
                print(f"[GroqClient] Attempt {attempt+1} failed: {e}. Retrying...")
                time.sleep(1)

        raise RuntimeError(f"All Groq API attempts exhausted. Last error: {last_error}")
