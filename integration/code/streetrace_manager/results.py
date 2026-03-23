"""Results module.

Responsibilities:
- Record race outcomes
- Update driver rankings
- Apply prize money to inventory cash balance
- Optionally mark a vehicle as damaged

Business rules:
- Race must exist.
- Winner must be among the race entries.
- A race can only be completed once.
- Prize money must be a non-negative integer.
"""

from __future__ import annotations

from .exceptions import ResultError, ValidationError
from .inventory import add_cash, mark_vehicle_damaged
from .race_management import get_race
from .models import RaceResult
from .store import DataStore


def record_race_result(
    store: DataStore,
    race_id: str,
    *,
    winner_driver: str,
    prize_money: int,
    damaged_vehicle_id: str | None = None,
) -> RaceResult:
    """Record a race result, update rankings, and apply prize money."""
    if not isinstance(prize_money, int):
        raise ValidationError("Prize money must be an integer")
    if prize_money < 0:
        raise ValidationError("Prize money must be non-negative")

    race = get_race(store, race_id)

    if race.status == "completed" or str(race_id) in store.results:
        raise ResultError(f"Race {race.race_id} already has a recorded result")

    if not any(e.driver_name == winner_driver for e in race.entries):
        raise ResultError("Winner must be one of the race entries")

    # Apply money to inventory
    add_cash(store, prize_money)

    # Rankings: count wins
    store.rankings[winner_driver] = store.rankings.get(winner_driver, 0) + 1

    # Optional vehicle damage tracking
    if damaged_vehicle_id is not None:
        mark_vehicle_damaged(store, damaged_vehicle_id)

    race.status = "completed"

    result = RaceResult(
        race_id=race.race_id,
        winner_driver=winner_driver,
        prize_money=prize_money,
        damaged_vehicle_id=damaged_vehicle_id,
    )
    store.results[race.race_id] = result
    return result


def get_rankings(store: DataStore) -> list[tuple[str, int]]:
    """Return rankings sorted by wins desc, then name asc."""
    return sorted(store.rankings.items(), key=lambda kv: (-kv[1], kv[0]))


def get_result(store: DataStore, race_id: str) -> RaceResult:
    rid = str(race_id).strip()
    result = store.results.get(rid)
    if result is None:
        raise ResultError(f"No recorded result for race '{race_id}'")
    return result
