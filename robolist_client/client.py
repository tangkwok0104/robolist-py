"""Robolist.ai Python client.

Fetches structured robot and company data from the Robolist.ai public
directory.  Every public page embeds schema.org JSON-LD; this client
extracts and parses that data so you never have to scrape raw HTML.

Robolist.ai tracks 4,600+ robots across 15+ categories:
  humanoid, industrial-arm, cobot, amr-warehouse, agv, quadruped,
  surgical-medical, delivery, hospitality-service, agricultural,
  cleaning, exoskeleton, and more.

Example::

    from robolist_client import RobolistClient

    with RobolistClient() as client:
        robot = client.get_robot("unitree-h1")
        print(robot.name, robot.score)

        company = client.get_company("unitree-robotics")
        for r in company.robots:
            print(r.name, r.url)
"""

from __future__ import annotations

import json
import re
from typing import Optional

import httpx

from .exceptions import NotFoundError, ParseError, RateLimitError, RobolistError
from .models import Company, Robot, RobotSummary

BASE_URL = "https://www.robolist.ai"
_DEFAULT_UA = "robolist-client/0.1.0 (+https://github.com/tangkwok0104/robolist-py)"
_LD_PATTERN = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)


def _extract_ld(html: str, type_name: str) -> dict:
    """Return the first JSON-LD block whose @type matches *type_name*."""
    for raw in _LD_PATTERN.findall(html):
        try:
            obj = json.loads(raw.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        candidates = obj if isinstance(obj, list) else [obj]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == type_name:
                return candidate
    raise ParseError(f"No JSON-LD block with @type={type_name!r} found in page")


class RobolistClient:
    """Synchronous client for the Robolist.ai public data.

    Parameters
    ----------
    timeout:
        HTTP request timeout in seconds.
    base_url:
        Override the base URL (useful for testing against a local dev server).

    Usage::

        client = RobolistClient()
        robot = client.get_robot("boston-dynamics-spot")
        client.close()

        # Or as a context manager:
        with RobolistClient() as client:
            robot = client.get_robot("boston-dynamics-spot")
    """

    def __init__(
        self,
        timeout: float = 30.0,
        base_url: str = BASE_URL,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": _DEFAULT_UA},
            follow_redirects=True,
        )

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> "RobolistClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_html(self, path: str) -> str:
        url = f"{self.base_url}{path}"
        try:
            resp = self._http.get(url)
        except httpx.TransportError as exc:
            raise RobolistError(f"Network error fetching {url}: {exc}") from exc
        if resp.status_code == 404:
            raise NotFoundError(f"Not found: {path}")
        if resp.status_code == 429:
            raise RateLimitError("Rate limit — back off and retry")
        if not resp.is_success:
            raise RobolistError(f"HTTP {resp.status_code} for {url}")
        return resp.text

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_robot(self, slug: str) -> Robot:
        """Fetch structured data for a robot by its URL slug.

        Parameters
        ----------
        slug:
            The slug portion of the robot's Robolist URL, e.g.
            ``"unitree-h1"`` for ``https://www.robolist.ai/robots/unitree-h1``.

        Returns
        -------
        Robot
            Parsed robot record.

        Raises
        ------
        NotFoundError
            If no robot exists with this slug.
        ParseError
            If the page exists but contains no Product JSON-LD.
        """
        html = self._get_html(f"/robots/{slug}")
        data = _extract_ld(html, "Product")

        price_usd: Optional[float] = None
        price_currency = "USD"
        offers = data.get("offers")
        if isinstance(offers, dict):
            try:
                price_usd = float(offers["price"])
                price_currency = offers.get("priceCurrency", "USD")
            except (KeyError, TypeError, ValueError):
                pass

        score: Optional[float] = None
        ar = data.get("aggregateRating")
        if isinstance(ar, dict):
            try:
                score = float(ar["ratingValue"])
            except (KeyError, TypeError, ValueError):
                pass

        brand = data.get("brand") or {}

        return Robot(
            slug=slug,
            name=data.get("name", ""),
            url=f"{self.base_url}/robots/{slug}",
            manufacturer=brand.get("name", "") if isinstance(brand, dict) else "",
            manufacturer_url=brand.get("url", "") if isinstance(brand, dict) else "",
            description=data.get("description"),
            image_url=data.get("image"),
            price_usd=price_usd,
            price_currency=price_currency,
            score=score,
            raw=data,
        )

    def get_company(self, slug: str) -> Company:
        """Fetch structured data for a company by its URL slug.

        Parameters
        ----------
        slug:
            The slug portion of the company's Robolist URL, e.g.
            ``"boston-dynamics"`` for
            ``https://www.robolist.ai/companies/boston-dynamics``.

        Returns
        -------
        Company
            Parsed company record including a list of its robots.

        Raises
        ------
        NotFoundError
            If no company exists with this slug.
        ParseError
            If the page exists but contains no Organization JSON-LD.
        """
        html = self._get_html(f"/companies/{slug}")
        data = _extract_ld(html, "Organization")

        robots: list[RobotSummary] = []
        members = data.get("member") or []
        if isinstance(members, list):
            for item in members:
                if not isinstance(item, dict):
                    continue
                robot_url = item.get("url", "")
                robot_slug = robot_url.rstrip("/").split("/")[-1] if robot_url else ""
                robots.append(
                    RobotSummary(
                        slug=robot_slug,
                        name=item.get("name", ""),
                        url=robot_url,
                        company=slug,
                    )
                )

        same_as = data.get("sameAs") or []
        if isinstance(same_as, str):
            same_as = [same_as]

        return Company(
            slug=slug,
            name=data.get("name", ""),
            url=f"{self.base_url}/companies/{slug}",
            description=data.get("description"),
            website=data.get("url"),
            logo_url=data.get("logo"),
            same_as=same_as if isinstance(same_as, list) else [],
            robots=robots,
            raw=data,
        )
