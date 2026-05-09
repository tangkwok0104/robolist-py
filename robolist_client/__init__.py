"""robolist-client — Python client for Robolist.ai.

Robolist.ai is the independent robotics industry directory and leaderboard,
tracking 4,600+ robots and the companies that make them.

    https://www.robolist.ai
"""

from .client import RobolistClient
from .exceptions import NotFoundError, ParseError, RateLimitError, RobolistError
from .models import Company, Robot, RobotSummary

__version__ = "0.1.0"
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
