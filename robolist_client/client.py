"""Robolist.ai Python client.

Fetches structured robot and company data from the Robolist.ai public
directory.  Every public page embeds schema.org JSON-LD; the
page-specific nodes (Product, Organization, CollectionPage) live inside
a top-level ``@graph`` block.  This client flattens that graph and
parses the nodes so you never have to scrape raw HTML.

Robolist.ai ranks robots by the **Robo Index** — an objective, uncapped
0–100 score derived from structured spec data (not user reviews, not
paid placement).  The Robo Index is shown on each page but is not
currently published in the JSON-LD, so ``Robot.score`` is usually
``None``; open ``Robot.url`` for the live value.

Example::

    from robolist_client import RobolistClient

    with RobolistClient() as client:
        robot = client.get_robot("boston-dynamics-spot")
        print(robot.name, robot.price_usd, robot.category)

        company = client.get_company("unitree")
        for r in company.robots:
            print(r.name, r.url)
"""

from __future__ import annotations

import json
import re
from typing import Callable, Iterator, Optional

import httpx

from .exceptions import NotFoundError, ParseError, RateLimitError, RobolistError
from .models import Company, Robot, RobotSummary

BASE_URL = "https://www.robolist.ai"
_VERSION = "0.2.0"
_DEFAULT_UA = f"robolist-client/{_VERSION} (+https://github.com/tangkwok0104/robolist-py)"
_LD_PATTERN = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)


def _iter_ld_nodes(html: str) -> Iterator[dict]:
    """Yield every schema.org node embedded in the page.

    Robolist emits a few ``<script type="application/ld+json">`` blocks.
    Page-specific data (Product, Organization, CollectionPage) is wrapped
    in a top-level ``{"@graph": [...]}`` block, while the site-wide
    Organization / WebSite blocks are flat.  This helper flattens both
    shapes so callers can scan one stream of nodes.  Nested objects
    (e.g. a Product's ``brand``) are intentionally not recursed into.
    """
    for raw in _LD_PATTERN.findall(html):
        try:
            obj = json.loads(raw.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        roots = obj if isinstance(obj, list) else [obj]
        for root in roots:
            if not isinstance(root, dict):
                continue
            graph = root.get("@graph")
            if isinstance(graph, list):
                for node in graph:
                    if isinstance(node, dict):
                        yield node
            else:
                yield root


def _find_node(html: str, predicate: Callable[[dict], bool]) -> Optional[dict]:
    """Return the first embedded JSON-LD node satisfying *predicate*."""
    for node in _iter_ld_nodes(html):
        if predicate(node):
            return node
    return None


def _slug_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1] if url else ""


def _parse_offer(offers: object) -> tuple[Optional[float], str]:
    if isinstance(offers, dict):
        try:
            return float(offers["price"]), str(offers.get("priceCurrency", "USD"))
        except (KeyError, TypeError, ValueError):
            pass
    return None, "USD"


def _parse_rating(aggregate_rating: object) -> Optional[float]:
    if isinstance(aggregate_rating, dict):
        try:
            return float(aggregate_rating["ratingValue"])
        except (KeyError, TypeError, ValueError):
            pass
    return None


def _year_from_date(value: object) -> Optional[int]:
    if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
        return int(value[:4])
    return None


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
            ``"boston-dynamics-spot"`` for
            ``https://www.robolist.ai/robots/boston-dynamics-spot``.
            Old or merged slugs redirect transparently; the returned
            ``Robot.slug`` is always the canonical one.

        Returns
        -------
        Robot
            Parsed robot record.

        Raises
        ------
        NotFoundError
            If no robot exists with this slug.
        ParseError
            If the page exists but exposes no Product JSON-LD (e.g. a
            sparse record, or a page whose cache predates structured
            data).  Open the page URL directly in that case.
        """
        html = self._get_html(f"/robots/{slug}")
        product = _find_node(html, lambda n: n.get("@type") == "Product")
        if product is None:
            raise ParseError(
                f"No Product structured data found for robot {slug!r}"
            )

        canonical_url = (
            product.get("@id")
            or product.get("url")
            or f"{self.base_url}/robots/{slug}"
        )

        brand = product.get("brand")
        brand = brand if isinstance(brand, dict) else {}

        price_usd, price_currency = _parse_offer(product.get("offers"))

        country = product.get("countryOfOrigin")
        country_name = country.get("name") if isinstance(country, dict) else None

        return Robot(
            slug=_slug_from_url(canonical_url),
            name=product.get("name", ""),
            url=canonical_url,
            manufacturer=brand.get("name", ""),
            manufacturer_url=brand.get("url", ""),
            description=product.get("description"),
            image_url=product.get("image"),
            category=product.get("category"),
            country_of_origin=country_name,
            launch_year=_year_from_date(product.get("releaseDate")),
            date_modified=product.get("dateModified"),
            price_usd=price_usd,
            price_currency=price_currency,
            score=_parse_rating(product.get("aggregateRating")),
            raw=product,
        )

    def get_company(self, slug: str) -> Company:
        """Fetch structured data for a company by its URL slug.

        Parameters
        ----------
        slug:
            The slug portion of the company's Robolist URL, e.g.
            ``"boston-dynamics"`` for
            ``https://www.robolist.ai/companies/boston-dynamics``.
            Old or merged slugs redirect transparently.

        Returns
        -------
        Company
            Parsed company record including a list of its robots.

        Raises
        ------
        NotFoundError
            If no company exists with this slug.
        ParseError
            If the page exists but exposes no company Organization JSON-LD.
        """
        html = self._get_html(f"/companies/{slug}")
        nodes = list(_iter_ld_nodes(html))

        # The company Organization is identified by its @id pointing at a
        # /companies/ URL — this skips the site-wide "Robolist.ai"
        # Organization block that appears on every page.
        org = next(
            (
                n
                for n in nodes
                if n.get("@type") == "Organization"
                and "/companies/" in str(n.get("@id", ""))
            ),
            None,
        )
        if org is None:
            raise ParseError(
                f"No company Organization structured data found for {slug!r}"
            )

        canonical_url = org.get("@id") or f"{self.base_url}/companies/{slug}"
        canonical_slug = _slug_from_url(canonical_url)

        # Robots live in the page's CollectionPage → mainEntity (ItemList).
        robots: list[RobotSummary] = []
        collection = next(
            (n for n in nodes if n.get("@type") == "CollectionPage"), None
        )
        if collection is not None:
            main_entity = collection.get("mainEntity")
            items = (
                main_entity.get("itemListElement")
                if isinstance(main_entity, dict)
                else None
            )
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    robot_url = item.get("url", "")
                    robots.append(
                        RobotSummary(
                            slug=_slug_from_url(robot_url),
                            name=item.get("name", ""),
                            url=robot_url,
                            company=canonical_slug,
                            position=item.get("position"),
                        )
                    )

        address = org.get("address")
        address = address if isinstance(address, dict) else {}

        same_as = org.get("sameAs") or []
        if isinstance(same_as, str):
            same_as = [same_as]

        return Company(
            slug=canonical_slug,
            name=org.get("name", ""),
            url=canonical_url,
            description=org.get("description"),
            website=org.get("url"),
            logo_url=org.get("logo"),
            founding_date=org.get("foundingDate"),
            country=address.get("addressCountry"),
            same_as=same_as if isinstance(same_as, list) else [],
            robots=robots,
            raw=org,
        )
