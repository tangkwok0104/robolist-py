from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RobotSummary:
    """Lightweight robot reference as seen inside a company or category listing."""

    slug: str
    name: str
    url: str
    company: str = ""
    category: str = ""


@dataclass
class Robot:
    """Full robot data extracted from the Robolist.ai Product JSON-LD.

    All fields map 1-to-1 to schema.org/Product properties published on
    every ``/robots/<slug>`` page.  Access ``raw`` for any field not
    surfaced here.
    """

    slug: str
    name: str
    url: str
    manufacturer: str
    manufacturer_url: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price_usd: Optional[float] = None
    price_currency: str = "USD"
    score: Optional[float] = None
    raw: dict = field(default_factory=dict, repr=False)


@dataclass
class Company:
    """Company data extracted from the Robolist.ai Organization JSON-LD.

    Maps to schema.org/Organization on every ``/companies/<slug>`` page.
    """

    slug: str
    name: str
    url: str
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    same_as: list[str] = field(default_factory=list)
    robots: list[RobotSummary] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)
