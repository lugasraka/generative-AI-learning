"""
Part 1 — Introduction to LLM Agents: Agent Loop Demo

Simulates the sense-decide-act-observe loop for a vacation planner
without any LLM calls. Demonstrates the core agent concept.

Run:  python agent_loop_demo.py
"""

import json
import sys


# ---------- Mock tools ----------


def search_flights(destination: str, budget: int) -> dict:
    """Mock flight search returning cheapest option within budget."""
    flights = {
        "Tokyo": {"airline": "ANA", "price": 850, "duration": "14h"},
        "Patagonia": {"airline": "LATAM", "price": 1100, "duration": "18h"},
        "Paris": {"airline": "Air France", "price": 600, "duration": "8h"},
    }
    result = flights.get(
        destination, {"airline": "Unknown", "price": budget, "duration": "N/A"}
    )
    within = result["price"] <= budget
    return {"found": within, **result}


def search_hotels(destination: str, nights: int, budget_per_night: int) -> dict:
    """Mock hotel search returning cheapest option within budget."""
    hotels = {
        "Tokyo": {"name": "Shinjuku Inn", "price_per_night": 95},
        "Patagonia": {"name": "Mountain Lodge", "price_per_night": 120},
        "Paris": {"name": "Le Petit Hotel", "price_per_night": 110},
    }
    base = hotels.get(
        destination, {"name": "Generic Hotel", "price_per_night": budget_per_night}
    )
    total = base["price_per_night"] * nights
    within = total <= budget_per_night * nights
    return {"found": within, "total": total, **base}


def search_activities(destination: str, days: int) -> list:
    """Mock activity search returning a list of options."""
    activities = {
        "Tokyo": [
            {"name": "Senso-ji Temple", "cost": 0},
            {"name": "Tsukiji Fish Market", "cost": 20},
            {"name": "Mt. Fuji Day Trip", "cost": 150},
            {"name": "Akihabara Tour", "cost": 30},
            {"name": "Sushi Making Class", "cost": 80},
        ],
        "Patagonia": [
            {"name": "Torres del Paine Trek", "cost": 50},
            {"name": "Glacier Boat Tour", "cost": 80},
            {"name": "Horseback Riding", "cost": 60},
        ],
        "Paris": [
            {"name": "Eiffel Tower", "cost": 25},
            {"name": "Louvre Museum", "cost": 17},
            {"name": "Seine River Cruise", "cost": 15},
        ],
    }
    return activities.get(destination, [{"name": "Walking Tour", "cost": 0}])


# ---------- Agent loop ----------


def run_agent(goal: dict) -> tuple[list[dict], dict]:
    """Run the sense-decide-act-observe loop until plan is complete."""
    state = {
        "destination": goal["destination"],
        "days": goal["days"],
        "budget": goal["budget"],
        "flights": None,
        "hotel": None,
        "activities": [],
        "spent": 0,
    }
    transcript = []

    def sense() -> dict:
        remaining = state["budget"] - state["spent"]
        days_done = len(state["activities"])
        return {
            "remaining_budget": remaining,
            "days_with_activities": days_done,
            "needs_flights": state["flights"] is None,
            "needs_hotel": state["hotel"] is None,
            "needs_activities": days_done < state["days"],
        }

    def decide(perception: dict) -> str:
        if perception["needs_flights"]:
            return "search_flights"
        if perception["needs_hotel"]:
            return "search_hotels"
        if perception["needs_activities"]:
            return "search_activities"
        return "done"

    def act(action: str) -> dict:
        dest = state["destination"]
        if action == "search_flights":
            remaining_after = state["budget"] - state["spent"]
            return search_flights(dest, remaining_after)
        if action == "search_hotels":
            remaining_after = state["budget"] - state["spent"]
            nights = state["days"] - 1
            budget_per_night = remaining_after // max(nights, 1)
            return search_hotels(dest, nights, budget_per_night)
        if action == "search_activities":
            return {"activities": search_activities(dest, state["days"])}
        return {}

    def observe(action: str, result: dict) -> str:
        if action == "search_flights":
            if result.get("found"):
                state["flights"] = result
                state["spent"] += result["price"]
                return f"Found flight: {result['airline']} for ${result['price']}"
            return "No flights within budget"
        if action == "search_hotels":
            if result.get("found"):
                state["hotel"] = result
                state["spent"] += result["total"]
                return f"Found hotel: {result['name']} for ${result['total']}"
            return "No hotels within budget"
        if action == "search_activities":
            chosen = result["activities"][: state["days"] - len(state["activities"])]
            for act in chosen:
                if state["spent"] + act["cost"] <= state["budget"]:
                    state["activities"].append(act)
                    state["spent"] += act["cost"]
            names = [a["name"] for a in state["activities"]]
            return f"Booked activities: {', '.join(names)}"
        return "Plan complete"

    # Main loop
    step = 0
    while step < 20:
        step += 1
        perception = sense()
        action = decide(perception)
        if action == "done":
            entry = {
                "step": step,
                "action": "done",
                "perception": perception,
                "result": "Plan complete",
            }
            transcript.append(entry)
            break
        result = act(action)
        msg = observe(action, result)
        entry = {
            "step": step,
            "action": action,
            "perception": perception,
            "result": msg,
            "budget_remaining": state["budget"] - state["spent"],
        }
        transcript.append(entry)

    return transcript, state


# ---------- Display ----------


def print_transcript(transcript: list, final_state: dict) -> None:
    print("=" * 60)
    print("  AGENT LOOP TRANSCRIPT")
    print("=" * 60)
    for entry in transcript:
        step = entry["step"]
        action = entry["action"]
        result = entry["result"]
        remaining = entry.get("budget_remaining", "—")
        print(f"\n  Step {step}: {action}")
        print(f"    Result:    {result}")
        if remaining != "—":
            print(f"    Remaining: ${remaining}")
    print("\n" + "=" * 60)
    print("  FINAL PLAN")
    print("=" * 60)
    print(f"  Destination:  {final_state['destination']}")
    print(f"  Days:         {final_state['days']}")
    print(f"  Total spent:  ${final_state['spent']} / ${final_state['budget']}")
    if final_state["flights"]:
        f = final_state["flights"]
        print(f"  Flight:       {f['airline']} — ${f['price']}")
    if final_state["hotel"]:
        h = final_state["hotel"]
        print(f"  Hotel:        {h['name']} — ${h['total']}")
    act_names = [a["name"] for a in final_state["activities"]]
    print(f"  Activities:   {', '.join(act_names) if act_names else 'none'}")
    print("=" * 60)


# ---------- Main ----------


def main() -> None:
    goals = [
        {"destination": "Tokyo", "days": 3, "budget": 1500},
        {"destination": "Patagonia", "days": 5, "budget": 2000},
    ]

    for goal in goals:
        print(
            f"\n>>> Goal: Plan a {goal['days']}-day trip to {goal['destination']} "
            f"under ${goal['budget']}\n"
        )
        transcript, final_state = run_agent(goal)
        print_transcript(transcript, final_state)
        print()


if __name__ == "__main__":
    main()
