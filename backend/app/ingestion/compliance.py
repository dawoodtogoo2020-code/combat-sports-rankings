"""
Ethical scraping compliance layer.
Checks robots.txt, enforces rate limits, and identifies the bot properly.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = "CSRankingsBot/1.0 (+https://combat-sports-rankings.pages.dev; competition results aggregator)"


class RobotsChecker:
    """Fetches and caches robots.txt per domain."""

    def __init__(self, cache_ttl_hours: int = 24):
        self._cache: dict[str, tuple[RobotFileParser, float]] = {}
        self._cache_ttl = cache_ttl_hours * 3600

    async def is_allowed(self, url: str) -> bool:
        domain = self._get_domain(url)
        parser = await self._get_parser(domain)
        if parser is None:
            # Could not fetch robots.txt — assume allowed but log it
            logger.warning(f"Could not fetch robots.txt for {domain}, assuming allowed")
            return True
        return parser.can_fetch(USER_AGENT, url)

    async def get_status(self, url: str) -> str:
        """Returns 'allowed', 'disallowed', or 'unknown'."""
        domain = self._get_domain(url)
        parser = await self._get_parser(domain)
        if parser is None:
            return "unknown"
        return "allowed" if parser.can_fetch(USER_AGENT, url) else "disallowed"

    async def _get_parser(self, domain: str) -> RobotFileParser | None:
        cached = self._cache.get(domain)
        if cached and (time.time() - cached[1]) < self._cache_ttl:
            return cached[0]

        robots_url = f"https://{domain}/robots.txt"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(robots_url, follow_redirects=True)
                if resp.status_code == 200:
                    parser = RobotFileParser()
                    parser.parse(resp.text.splitlines())
                    self._cache[domain] = (parser, time.time())
                    logger.info(f"Fetched robots.txt for {domain}")
                    return parser
                else:
                    # No robots.txt = no restrictions
                    parser = RobotFileParser()
                    parser.allow_all = True
                    self._cache[domain] = (parser, time.time())
                    return parser
        except Exception as e:
            logger.error(f"Failed to fetch robots.txt for {domain}: {e}")
            return None

    @staticmethod
    def _get_domain(url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split("/")[0]


class RateLimiter:
    """Per-domain rate limiter. Default: 1 request per second."""

    def __init__(self, requests_per_second: float = 1.0):
        self._min_interval = 1.0 / requests_per_second
        self._last_request: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def wait(self, domain: str) -> None:
        async with self._lock:
            now = time.time()
            last = self._last_request.get(domain, 0)
            elapsed = now - last
            if elapsed < self._min_interval:
                delay = self._min_interval - elapsed
                await asyncio.sleep(delay)
            self._last_request[domain] = time.time()


class ComplianceChecker:
    """Combines robots.txt checking and rate limiting."""

    def __init__(self, requests_per_second: float = 1.0):
        self.robots = RobotsChecker()
        self.rate_limiter = RateLimiter(requests_per_second)

    async def check_and_wait(self, url: str) -> bool:
        """Check robots.txt and wait for rate limit. Returns True if request is allowed."""
        allowed = await self.robots.is_allowed(url)
        if not allowed:
            logger.warning(f"Blocked by robots.txt: {url}")
            return False

        domain = urlparse(url).netloc
        await self.rate_limiter.wait(domain)
        return True

    async def get_robots_status(self, url: str) -> str:
        return await self.robots.get_status(url)
