"""Registration module.

Responsibilities:
- Register new crew members (name + role)
- Provide lookup and listing functions

Business rules:
- No duplicate crew member names (case-insensitive)
- Name must be non-empty
- Role must be non-empty
"""

from __future__ import annotations

from .exceptions import CrewMemberNotFoundError, DuplicateCrewMemberError, ValidationError
from .models import CrewMember
from .store import DataStore


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def register_member(store: DataStore, name: str, role: str) -> CrewMember:
    """Register a new crew member.

    Args:
        store: Shared datastore.
        name: Crew member display name.
        role: Initial role.

    Returns:
        The created CrewMember.

    Raises:
        ValidationError: on empty name/role.
        DuplicateCrewMemberError: if the name already exists.
    """
    if name is None or not str(name).strip():
        raise ValidationError("Crew member name must be non-empty")
    if role is None or not str(role).strip():
        raise ValidationError("Crew member role must be non-empty")

    key = _normalize_name(str(name))
    if key in store.crew:
        raise DuplicateCrewMemberError(f"Crew member '{name}' is already registered")

    member = CrewMember(name=str(name).strip(), role=str(role).strip())
    store.crew[key] = member
    return member


def get_member(store: DataStore, name: str) -> CrewMember:
    """Get a registered crew member by name.

    Raises:
        CrewMemberNotFoundError: if no member exists with this name.
    """
    key = _normalize_name(str(name))
    member = store.crew.get(key)
    if member is None:
        raise CrewMemberNotFoundError(f"Crew member '{name}' not found")
    return member


def list_members(store: DataStore) -> list[CrewMember]:
    """Return all registered crew members in registration order."""
    return list(store.crew.values())
