from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RobotSummary:
    """Lightweight robot reference as seen inside a company listing."""

    slug: str
    name: str
    url: str
    company: str = ""
    category: str = ""
    position: Optional[int] = None


@dataclass
class Robot:
    """Full robot data extracted from the Robolist.ai Product JSON-LD.

    Fields map to the schema.org/Product node published inside the
    ``@graph`` block on every ``/robots/<slug>`` page.  Access ``raw``
    for any field not surfaced here.

    Note on ``score``: Robolist ranks robots by the **Robo Index** (an
    objective, uncapped 0–100 score).  The Robo Index is shown on each
    robot's page but is **not** currently published in the page's
    JSON-LD, so ``score`` is best-effort and is usually ``None``.  Open
    ``url`` to read the live Robo Index.
    """

    slug: str
    name: str
    url: str
    manufacturer: str
    manufacturer_url: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    country_of_origin: Optional[str] = None
    launch_year: Optional[int] = None
    date_modified: Optional[str] = None
    price_usd: Optional[float] = None
    price_currency: str = "USD"
    score: Optional[float] = None
    raw: dict = field(default_factory=dict, repr=False)


@dataclass
class Company:
    """Company data extracted from the Robolist.ai page JSON-LD.

    Company metadata comes from the schema.org/Organization node (matched
    by its ``@id``, which points at the company's Robolist page).  The
    list of robots comes from the page's CollectionPage → ItemList.
    """

    slug: str
    name: str
    url: str
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    founding_date: Optional[str] = None
    country: Optional[str] = None
    same_as: list[str] = field(default_factory=list)
    robots: list[RobotSummary] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)
