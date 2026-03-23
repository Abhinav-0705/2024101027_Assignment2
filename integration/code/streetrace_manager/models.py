"""Domain models for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass


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
