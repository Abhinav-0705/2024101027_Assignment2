"""In-memory datastore for StreetRace Manager.

Kept intentionally simple: a single store instance can be passed around
between modules to support integration testing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import CrewMember, Race, Vehicle


@dataclass(slots=True)
class DataStore:
    """Holds all system state for StreetRace Manager."""

    crew: dict[str, CrewMember] = field(default_factory=dict)

    # Extra roles assigned via crew_management (in addition to CrewMember.role).
    # Keyed by CrewMember.name to preserve original display casing.
    crew_roles: dict[str, set[str]] = field(default_factory=dict)

    # Skill levels per member per role (role keys are lowercased).
    # Example: crew_skills["Alice"]["driver"] == 7
    crew_skills: dict[str, dict[str, int]] = field(default_factory=dict)

    # Inventory state
    cash_balance: int = 0
    vehicles: dict[str, Vehicle] = field(default_factory=dict)
    parts: dict[str, int] = field(default_factory=dict)
    tools: dict[str, int] = field(default_factory=dict)

    # Race management state
    races: dict[str, Race] = field(default_factory=dict)
    next_race_id: int = 1
