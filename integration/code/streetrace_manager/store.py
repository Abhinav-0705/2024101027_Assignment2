"""In-memory datastore for StreetRace Manager.

Kept intentionally simple: a single store instance can be passed around
between modules to support integration testing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import CrewMember


@dataclass(slots=True)
class DataStore:
    """Holds all system state for StreetRace Manager."""

    crew: dict[str, CrewMember] = field(default_factory=dict)
