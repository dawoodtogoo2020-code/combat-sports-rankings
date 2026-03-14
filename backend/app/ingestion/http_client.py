"""
HTTP client wrapper that enforces compliance (robots.txt + rate limiting) on every request.
"""

import logging
from typing import Optional

import httpx

from app.ingestion.compliance import ComplianceChecker, USER_AGENT

logger = logging.getLogger(__name__)


class ScraperHttpClient:
    """HTTP client that goes through compliance checking for every request."""

    def __init__(self, compliance: ComplianceChecker | None = None):
        self.compliance = compliance or ComplianceChecker()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def get(self, url: str) -> Optional[httpx.Response]:
        """GET request with compliance check. Returns None if blocked."""
        allowed = await self.compliance.check_and_wait(url)
        if not allowed:
            return None

        try:
            resp = await self._client.get(url)
            logger.debug(f"GET {url} -> {resp.status_code}")
            return resp
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None

    async def get_json(self, url: str) -> Optional[dict]:
        """GET request expecting JSON response."""
        resp = await self.get(url)
        if resp and resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                logger.error(f"Failed to parse JSON from {url}")
        return None

    async def get_html(self, url: str) -> Optional[str]:
        """GET request expecting HTML response."""
        resp = await self.get(url)
        if resp and resp.status_code == 200:
            return resp.text
        return None
