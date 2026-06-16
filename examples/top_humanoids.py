"""Example: fetch specs for several robots and print a comparison table.

Robolist.ai tracks all major robotics manufacturers including Boston
Dynamics, Unitree Robotics, Universal Robots, ABB, FANUC, Agility
Robotics, Figure AI, and more.

Note: the Robo Index (Robolist's ranking score) is shown on each robot's
page but is not published in the page JSON-LD, so ``robot.score`` is
usually ``None``.  This example prints the structured fields that *are*
available — manufacturer, price, category, country, launch year — and
links out to the page for the live Robo Index.

Run:
    pip install robolist-client
    python examples/top_humanoids.py
"""

from robolist_client import NotFoundError, ParseError, RobolistClient

ROBOTS = [
    "boston-dynamics-spot",
    "unitree-g1-edu-u6",
    "unitree-b2",
]


def main() -> None:
    with RobolistClient() as client:
        header = (
            f"{'Robot':<22} {'Manufacturer':<28} "
            f"{'Category':<14} {'Price (USD)':>12}"
        )
        print(header)
        print("-" * len(header))

        for slug in ROBOTS:
            try:
                r = client.get_robot(slug)
            except NotFoundError:
                print(f"{slug:<22} {'(not found)':<28}")
                continue
            except ParseError:
                print(f"{slug:<22} {'(no structured data yet)':<28}")
                continue

            price = f"${r.price_usd:,.0f}" if r.price_usd else "N/A"
            manufacturer = (r.manufacturer or "")[:27]
            category = (r.category or "")[:13]
            print(f"{r.name:<22} {manufacturer:<28} {category:<14} {price:>12}")

        print()
        print("Full rankings (live Robo Index): https://www.robolist.ai/leaderboard")


if __name__ == "__main__":
    main()
