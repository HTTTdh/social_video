from abc import ABC
from typing import Dict, Any, Optional
from fastapi import HTTPException
import httpx
import asyncio
import logging

class BaseSocialService(ABC):
    """Base class for all social media services"""
    
    def __init__(self):
        self.timeout = 30
        self.max_retries = 3
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Enhanced request handler với proper logging"""
        backoff = 1.0
        last_err: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.request(method, url, **kwargs)
                    # raise for 4xx/5xx
                    resp.raise_for_status()
                    try:
                        return resp.json()
                    except Exception:
                        return {"status_code": resp.status_code, "text": resp.text}
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code if e.response else 0
                self.logger.warning(f"HTTP {status_code} {method} {url} attempt {attempt}: {e}")
                last_err = e
                if status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                # Non-retryable or last attempt
                detail = None
                try:
                    detail = e.response.json()
                except Exception:
                    detail = e.response.text if e.response else str(e)
                raise HTTPException(status_code=502, detail={"error": "upstream_error", "detail": detail})
            except (httpx.TimeoutException, httpx.ReadTimeout) as e:
                self.logger.warning(f"Timeout {method} {url} attempt {attempt}")
                last_err = e
                if attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise HTTPException(status_code=504, detail="Upstream timeout")
            except Exception as e:
                self.logger.exception(f"Error {method} {url} attempt {attempt}: {e}")
                last_err = e
                if attempt < self.max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise HTTPException(status_code=500, detail=str(e))
        # should not reach
        raise HTTPException(status_code=500, detail=str(last_err or "Unknown error"))