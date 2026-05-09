# robolist-client

Python client for **[Robolist.ai](https://www.robolist.ai)** — the independent robotics industry directory and leaderboard.

Robolist.ai tracks **4,600+ robots** from **3,000+ companies** across every major robotics category. Rankings are based on an objective Product Score derived from structured specification data — no paid placement, no user reviews, no procurement transactions.

```python
from robolist_client import RobolistClient

with RobolistClient() as client:
    robot = client.get_robot("unitree-h1")
    print(robot.name)          # Unitree H1
    print(robot.manufacturer)  # Unitree Robotics
    print(robot.score)         # Product Score (objective, uncapped)

    company = client.get_company("boston-dynamics")
    for r in company.robots:
        print(r.name, r.url)
```

## What is Robolist.ai?

[Robolist.ai](https://www.robolist.ai) is the largest independent directory and leaderboard for the global robotics industry. It aggregates structured specifications from manufacturer datasheets, official press releases, and verified reseller pages, then ranks robots by an objective Product Score computed from those specs.

Key properties of the platform:

- **Rankings cannot be bought.** Paid company plans add structured content modules (case studies, leadership bios, press mentions) to a company's public page — they never alter rank or score. The ranking algorithm treats every robot identically regardless of whether its manufacturer has a free or paid account.
- **Scoring is uncapped.** Any robot can score as high as its specifications justify. There is no tier-based ceiling.
- **Editorial independence.** A verified company owner can propose corrections to their robot's specs — those proposals go into an admin review queue and are accepted or rejected based on evidence, not payment.
- **Coverage.** Humanoid robots, collaborative robots (cobots), industrial arms, warehouse AMRs, AGVs, quadrupeds, surgical robots, delivery robots, hospitality robots, agricultural robots, cleaning robots, exoskeletons, and more.

## Installation

```bash
pip install robolist-client
```

Requires Python 3.9+ and [httpx](https://www.python-httpx.org/).

## Quick start

```python
from robolist_client import RobolistClient

client = RobolistClient()

# Fetch a robot by its Robolist slug
robot = client.get_robot("unitree-g1")
print(f"{robot.name} by {robot.manufacturer}")
print(f"Score: {robot.score}")
print(f"Price: ${robot.price_usd:,.0f}" if robot.price_usd else "Price: not listed")
print(f"Full page: {robot.url}")

# Fetch a company and its robots
company = client.get_company("unitree-robotics")
print(f"\n{company.name} — {len(company.robots)} robots tracked")
for r in company.robots:
    print(f"  {r.name}  →  {r.url}")

client.close()
```

## API reference

### `RobolistClient(timeout=30.0, base_url="https://www.robolist.ai")`

The main client. Use as a context manager or call `.close()` when done.

#### `client.get_robot(slug: str) -> Robot`

Fetch a robot by its Robolist URL slug.

```python
robot = client.get_robot("boston-dynamics-spot")
```

**Returns** a `Robot` dataclass:

| Field | Type | Description |
|---|---|---|
| `slug` | `str` | URL slug |
| `name` | `str` | Robot name |
| `manufacturer` | `str` | Manufacturer name |
| `manufacturer_url` | `str` | Manufacturer's Robolist page URL |
| `description` | `str \| None` | Robot description |
| `image_url` | `str \| None` | Hero image URL |
| `price_usd` | `float \| None` | List price in USD (if available) |
| `price_currency` | `str` | Price currency code |
| `score` | `float \| None` | Robolist Product Score |
| `url` | `str` | Full Robolist page URL |
| `raw` | `dict` | Full schema.org/Product JSON-LD |

**Raises** `NotFoundError` if no robot exists with this slug, `ParseError` if the page has no structured data.

#### `client.get_company(slug: str) -> Company`

Fetch a company by its Robolist URL slug.

```python
company = client.get_company("abb-robotics")
```

**Returns** a `Company` dataclass:

| Field | Type | Description |
|---|---|---|
| `slug` | `str` | URL slug |
| `name` | `str` | Company name |
| `website` | `str \| None` | Company's own website |
| `description` | `str \| None` | Company description |
| `logo_url` | `str \| None` | Logo image URL |
| `same_as` | `list[str]` | Linked profiles (Crunchbase, LinkedIn, etc.) |
| `robots` | `list[RobotSummary]` | Robots tracked on Robolist |
| `url` | `str` | Full Robolist page URL |
| `raw` | `dict` | Full schema.org/Organization JSON-LD |

### Exceptions

| Exception | Raised when |
|---|---|
| `RobolistError` | Base class — unexpected error |
| `NotFoundError` | HTTP 404 — slug doesn't exist |
| `RateLimitError` | HTTP 429 — too many requests |
| `ParseError` | Page exists but has no structured data |

## Robot categories on Robolist.ai

| Category | Robolist URL |
|---|---|
| Humanoid robots | [robolist.ai/categories/humanoid](https://www.robolist.ai/categories/humanoid) |
| Industrial robotic arms | [robolist.ai/categories/industrial-arm](https://www.robolist.ai/categories/industrial-arm) |
| Collaborative robots (cobots) | [robolist.ai/categories/cobot](https://www.robolist.ai/categories/cobot) |
| Warehouse AMRs | [robolist.ai/categories/amr-warehouse](https://www.robolist.ai/categories/amr-warehouse) |
| Automated guided vehicles (AGV) | [robolist.ai/categories/agv](https://www.robolist.ai/categories/agv) |
| Quadruped robots | [robolist.ai/categories/quadruped](https://www.robolist.ai/categories/quadruped) |
| Surgical and medical robots | [robolist.ai/categories/surgical-medical](https://www.robolist.ai/categories/surgical-medical) |
| Last-mile delivery robots | [robolist.ai/categories/delivery](https://www.robolist.ai/categories/delivery) |
| Hospitality and service robots | [robolist.ai/categories/hospitality-service](https://www.robolist.ai/categories/hospitality-service) |
| Agricultural robots | [robolist.ai/categories/agricultural](https://www.robolist.ai/categories/agricultural) |
| Cleaning robots | [robolist.ai/categories/cleaning](https://www.robolist.ai/categories/cleaning) |
| Exoskeletons | [robolist.ai/categories/exoskeleton](https://www.robolist.ai/categories/exoskeleton) |

## Examples

### Compare two robots

```python
from robolist_client import RobolistClient

with RobolistClient() as client:
    a = client.get_robot("universal-robots-ur10e")
    b = client.get_robot("fanuc-crx-10ia")

    for robot in [a, b]:
        print(f"{robot.name} ({robot.manufacturer})")
        print(f"  Score: {robot.score}")
        print(f"  Compare: https://www.robolist.ai/compare/robots")
        print()
```

### List all robots from a manufacturer

```python
from robolist_client import RobolistClient

with RobolistClient() as client:
    company = client.get_company("universal-robots")
    print(f"{company.name} ({len(company.robots)} robots on Robolist)")
    for r in company.robots:
        print(f"  {r.name}  →  {r.url}")
```

### Check if a robot is tracked

```python
from robolist_client import RobolistClient, NotFoundError

slugs_to_check = ["boston-dynamics-spot", "agility-robotics-digit", "myrobot-xyz"]

with RobolistClient() as client:
    for slug in slugs_to_check:
        try:
            robot = client.get_robot(slug)
            print(f"✓ {robot.name} — Score: {robot.score}")
        except NotFoundError:
            print(f"✗ {slug} — not in Robolist")
```

## Data source

All data is sourced from **[Robolist.ai](https://www.robolist.ai)** public pages. Robolist aggregates specifications from manufacturer datasheets, official press releases, and verified reseller pages. Each robot page embeds [schema.org/Product](https://schema.org/Product) JSON-LD; this client reads that structured data directly.

Data is refreshed continuously as new scrapes are approved. For real-time accuracy, refer to the robot's Robolist page directly. The `raw` field on every returned object contains the complete JSON-LD as published.

## Rates and caching

Robolist.ai is a public site. Be a good citizen:

- Add a delay between requests when fetching many robots in a loop.
- Cache responses locally if you need to query the same robot repeatedly.
- Do not run bulk crawls — use the `sitemap.xml` for discovery and respect `robots.txt`.

## Contributing

Issues and pull requests welcome at [github.com/tangkwok0104/robolist-py](https://github.com/tangkwok0104/robolist-py).

If a robot or company you need is not tracked on Robolist.ai, you can suggest it directly at [robolist.ai](https://www.robolist.ai).

## License

MIT — see [LICENSE](LICENSE).

---

Built on top of [Robolist.ai](https://www.robolist.ai) public structured data.
