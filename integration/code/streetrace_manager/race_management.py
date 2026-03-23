"""Race management module.

Responsibilities:
- Create races
- Enter drivers and vehicles into a race

Business rules:
- Driver must be registered.
- Only crew members with the 'driver' role may be entered.
- Vehicle must exist and must be in 'ok' condition.
- A vehicle can't be entered twice in the same race.
- A driver can't be entered twice in the same race.
"""

from __future__ import annotations

from .crew_management import has_role
from .exceptions import RaceEntryError, RaceNotFoundError, ValidationError
from .inventory import get_vehicle
from .models import Race, RaceEntry
from .store import DataStore


def create_race(store: DataStore, name: str) -> Race:
    if name is None or not str(name).strip():
        raise ValidationError("Race name must be non-empty")

    race_id = str(store.next_race_id)
    store.next_race_id += 1

    race = Race(race_id=race_id, name=str(name).strip())
    store.races[race_id] = race
    return race


def get_race(store: DataStore, race_id: str) -> Race:
    rid = str(race_id).strip()
    race = store.races.get(rid)
    if race is None:
        raise RaceNotFoundError(f"Race '{race_id}' not found")
    return race


def enter_race(store: DataStore, race_id: str, driver_name: str, vehicle_id: str) -> RaceEntry:
    race = get_race(store, race_id)

    # Validate driver
    if not has_role(store, driver_name, "driver"):
        raise RaceEntryError(f"'{driver_name}' is not eligible to race (not a driver)")

    # Validate vehicle
    vehicle = get_vehicle(store, vehicle_id)
    if vehicle.condition != "ok":
        raise RaceEntryError(f"Vehicle '{vehicle.vehicle_id}' is not available (condition={vehicle.condition})")

    # No duplicates
    for entry in race.entries:
        if entry.driver_name == driver_name:
            raise RaceEntryError(f"Driver '{driver_name}' is already entered in race {race.race_id}")
        if entry.vehicle_id == vehicle.vehicle_id:
            raise RaceEntryError(f"Vehicle '{vehicle.vehicle_id}' is already entered in race {race.race_id}")

    entry = RaceEntry(driver_name=driver_name, vehicle_id=vehicle.vehicle_id)
    race.entries.append(entry)
    return entry


def list_races(store: DataStore) -> list[Race]:
    return list(store.races.values())
