"""Example: fetch specs for several humanoid robots and compare them.

Robolist.ai tracks all major humanoid robot manufacturers including
Unitree Robotics, Agility Robotics, Figure AI, 1X Technologies,
Boston Dynamics, Fourier Intelligence, and more.

Run:
    pip install robolist-client
    python examples/top_humanoids.py
"""

from robolist_client import RobolistClient, NotFoundError

HUMANOIDS = [
    "unitree-h1",
    "agility-robotics-digit",
    "boston-dynamics-atlas",
]

def main() -> None:
    with RobolistClient() as client:
        print(f"{'Robot':<35} {'Manufacturer':<25} {'Score':>6}  {'Price (USD)':>12}")
        print("-" * 85)

        for slug in HUMANOIDS:
            try:
                r = client.get_robot(slug)
                price = f"${r.price_usd:,.0f}" if r.price_usd else "N/A"
                score = f"{r.score:.1f}" if r.score else "N/A"
                print(f"{r.name:<35} {r.manufacturer:<25} {score:>6}  {price:>12}")
            except NotFoundError:
                print(f"{slug:<35} {'not found':<25}")

        print()
        print("Full rankings: https://www.robolist.ai/categories/humanoid")


if __name__ == "__main__":
    main()
