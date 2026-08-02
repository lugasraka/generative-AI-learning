"""
Part 2 — What's Inside an Agent: The Harness

A minimal agent harness with all 4 components: Agent Core, Memory,
Tools, and Planning. Demonstrates how they wire together.

Run:  python mini_agent_harness.py
"""

import sys
import json
from pathlib import Path


# ---------- Tools ----------


def get_weather(city: str) -> dict:
    """Mock weather lookup."""
    data = {
        "Paris": {"temp_c": 18, "condition": "Partly cloudy", "wind_kph": 14},
        "Tokyo": {"temp_c": 24, "condition": "Sunny", "wind_kph": 8},
        "New York": {"temp_c": 22, "condition": "Clear", "wind_kph": 11},
    }
    return data.get(city, {"temp_c": 20, "condition": "Unknown", "wind_kph": 0})


def search_flights(origin: str, dest: str, date: str) -> dict:
    """Mock flight search."""
    routes = {
        ("London", "Paris"): {
            "airline": "Eurostar Air",
            "price": 120,
            "duration": "1h 15m",
        },
        ("New York", "Paris"): {"airline": "Delta", "price": 450, "duration": "7h 30m"},
        ("London", "Tokyo"): {"airline": "ANA", "price": 780, "duration": "12h"},
    }
    key = (origin, dest)
    return routes.get(key, {"airline": "Unknown", "price": 999, "duration": "N/A"})


def search_hotels(city: str, nights: int, max_per_night: int) -> dict:
    """Mock hotel search returning best option within budget."""
    hotels = {
        "Paris": [
            {"name": "Le Petit", "price_per_night": 85, "rating": 4.2},
            {"name": "Hotel Central", "price_per_night": 130, "rating": 4.5},
            {"name": "Grand Palace", "price_per_night": 250, "rating": 4.8},
        ],
        "Tokyo": [
            {"name": "Shinjuku Inn", "price_per_night": 70, "rating": 4.1},
            {"name": "Tokyo Tower Hotel", "price_per_night": 150, "rating": 4.6},
        ],
    }
    options = hotels.get(
        city, [{"name": "Generic", "price_per_night": 100, "rating": 3.5}]
    )
    within_budget = [h for h in options if h["price_per_night"] <= max_per_night]
    best = (
        max(within_budget, key=lambda h: h["rating"]) if within_budget else options[0]
    )
    best["total"] = best["price_per_night"] * nights
    return best


def search_activities(city: str, days: int, budget: int) -> list:
    """Mock activity search returning affordable options."""
    activities = {
        "Paris": [
            {"name": "Eiffel Tower", "cost": 25, "hours": 2},
            {"name": "Louvre Museum", "cost": 17, "hours": 3},
            {"name": "Seine Cruise", "cost": 15, "hours": 1},
            {"name": "Montmartre Walk", "cost": 0, "hours": 2},
            {"name": "Wine Tasting", "cost": 40, "hours": 2},
        ],
        "Tokyo": [
            {"name": "Senso-ji Temple", "cost": 0, "hours": 1},
            {"name": "Tsukiji Market", "cost": 20, "hours": 2},
            {"name": "Mt. Fuji Trip", "cost": 150, "hours": 8},
            {"name": "Akihabara Tour", "cost": 30, "hours": 3},
        ],
    }
    options = activities.get(city, [{"name": "Walking Tour", "cost": 0, "hours": 2}])
    affordable = [a for a in options if a["cost"] <= budget // max(days, 1)]
    return affordable[:days]


# ---------- Memory ----------


class Memory:
    """Short-term (dict) + long-term (list) memory."""

    def __init__(self) -> None:
        self.short_term: dict[str, object] = {}
        self.long_term: list[dict] = []

    def set_short(self, key: str, value: object) -> None:
        self.short_term[key] = value

    def get_short(self, key: str, default: object = None) -> object:
        return self.short_term.get(key, default)

    def append_long(self, summary: dict) -> None:
        self.long_term.append(summary)

    def summary(self) -> str:
        lines = ["  Short-term memory:"]
        for k, v in self.short_term.items():
            lines.append(f"    {k}: {v}")
        lines.append(f"  Long-term memory: {len(self.long_term)} past task(s)")
        for i, entry in enumerate(self.long_term):
            lines.append(
                f"    [{i + 1}] {entry.get('goal', 'unknown')} -> ${entry.get('spent', '?')}"
            )
        return "\n".join(lines)


# ---------- Planning ----------


def decompose(goal: str) -> list[str]:
    """Simple rule-based task decomposition."""
    tasks = []
    lower = goal.lower()
    if "flight" in lower or "trip" in lower or "weekend" in lower or "visit" in lower:
        tasks.append("search_flights")
    if "hotel" in lower or "stay" in lower or "weekend" in lower or "visit" in lower:
        tasks.append("search_hotels")
    if "activit" in lower or "do" in lower or "visit" in lower or "weekend" in lower:
        tasks.append("search_activities")
    if not tasks:
        tasks.append("search_activities")
    return tasks


def reflect(task: str, result: object) -> tuple[bool, str]:
    """Evaluate whether the result is acceptable."""
    if task == "search_flights":
        if isinstance(result, dict) and result.get("price", 999) < 900:
            return True, "Flight found within budget"
        return False, "Flight too expensive or not found"
    if task == "search_hotels":
        if isinstance(result, dict) and result.get("total", 9999) < 9999:
            return True, "Hotel found"
        return False, "No suitable hotel"
    if task == "search_activities":
        if isinstance(result, list) and len(result) > 0:
            return True, f"Found {len(result)} activities"
        return False, "No activities found"
    return True, "Done"


# ---------- Agent Core ----------


def run_agent(
    goal: str, origin: str, city: str, date: str, nights: int, budget: int
) -> dict:
    """The agent core: plan -> act -> reflect -> update memory -> repeat."""
    memory = Memory()
    memory.set_short("goal", goal)
    memory.set_short("budget", budget)
    memory.set_short("origin", origin)
    memory.set_short("destination", city)

    tasks = decompose(goal)
    memory.set_short("plan", tasks)

    tools_called = []
    log: list[dict] = []

    print(f"  Goal: {goal}")
    print(f"  Plan: {tasks}\n")

    for i, task in enumerate(tasks):
        print(f"  [{i + 1}/{len(tasks)}] Executing: {task}")

        if task == "search_flights":
            result = search_flights(origin, city, date)
        elif task == "search_hotels":
            max_per_night = budget // max(nights, 1) // 2
            result = search_hotels(city, nights, max_per_night)
        elif task == "search_activities":
            result = search_activities(city, nights, budget // 3)
        else:
            result = {}

        tools_called.append(task)
        ok, msg = reflect(task, result)
        print(f"    -> {msg}")

        if ok:
            memory.set_short(task, result)
        else:
            print(f"    -> Retrying with adjusted parameters...")
            if task == "search_flights":
                result = search_flights(origin, city, date)
                result["price"] = int(result["price"] * 0.9)
                memory.set_short(task, result)
                print(f"    -> Found alternative: {result}")

        log.append({"task": task, "success": ok, "result_summary": msg})
        print()

    # Calculate total cost
    total = 0
    flight = memory.get_short("search_flights", {})
    hotel = memory.get_short("search_hotels", {})
    activities = memory.get_short("search_activities", [])
    total += flight.get("price", 0)
    total += hotel.get("total", 0)
    total += sum(a.get("cost", 0) for a in activities)

    # Save to long-term memory
    memory.append_long({"goal": goal, "spent": total, "tasks": tools_called})

    return {
        "goal": goal,
        "total_cost": total,
        "budget": budget,
        "under_budget": total <= budget,
        "tools_called": tools_called,
        "memory": memory,
        "log": log,
    }


# ---------- Main ----------


def main() -> None:
    print("=" * 60)
    print("  MINIMAL AGENT HARNESS — 4 Components Demo")
    print("=" * 60)

    results = []

    # Task 1
    print("\n--- Task 1 ---")
    r1 = run_agent(
        goal="Plan a weekend in Paris under $800",
        origin="London",
        city="Paris",
        date="2026-09-15",
        nights=2,
        budget=800,
    )
    results.append(r1)

    # Task 2
    print("\n--- Task 2 ---")
    r2 = run_agent(
        goal="Plan a 3-day visit to Tokyo under $1500",
        origin="New York",
        city="Tokyo",
        date="2026-10-01",
        nights=3,
        budget=1500,
    )
    results.append(r2)

    # Summary
    print("=" * 60)
    print("  HARNESS SUMMARY")
    print("=" * 60)
    for r in results:
        status = "UNDER" if r["under_budget"] else "OVER"
        print(f"\n  Goal: {r['goal']}")
        print(f"  Total: ${r['total_cost']} / ${r['budget']} ({status} budget)")
        print(f"  Tools called: {', '.join(r['tools_called'])}")

    # Memory state
    print(f"\n{results[-1]['memory'].summary()}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
