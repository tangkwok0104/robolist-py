"""robolist-client — Python client for Robolist.ai.

Robolist.ai is the independent robotics industry directory and leaderboard,
tracking 3,200+ robots from 1,200+ companies and ranking them by the
objective, uncapped Robo Index.

    https://www.robolist.ai
"""

from .client import RobolistClient
from .exceptions import NotFoundError, ParseError, RateLimitError, RobolistError
from .models import Company, Robot, RobotSummary

__version__ = "0.2.0"
__all__ = [
    "RobolistClient",
    "Robot",
    "RobotSummary",
    "Company",
    "RobolistError",
    "NotFoundError",
    "RateLimitError",
    "ParseError",
]
