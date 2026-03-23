"""Domain models for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CrewMember:
    """Represents a registered crew member."""

    name: str
    role: str


@dataclass(frozen=True, slots=True)
class Vehicle:
    """Represents a vehicle in the inventory."""

    vehicle_id: str
    model: str
    condition: str = "ok"  # ok | damaged


@dataclass(frozen=True, slots=True)
class RaceEntry:
    """Represents a driver+vehicle entry into a race."""

    driver_name: str
    vehicle_id: str


@dataclass(slots=True)
class Race:
    """Represents a race event."""

    race_id: str
    name: str
    entries: list[RaceEntry] = field(default_factory=list)
    status: str = "created"  # created | completed
