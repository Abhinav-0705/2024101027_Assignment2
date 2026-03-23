"""Crew management module.

Responsibilities:
- Manage crew roles (driver, mechanic, strategist, etc.)
- Maintain skill levels per member per role

Business rules:
- A crew member must be registered before roles/skills can be modified.
- Role names must be non-empty.
- Skill levels must be integers in the range 0..10.

Design note:
Registration stores an initial role on the CrewMember record. Crew management
adds additional roles and skills in the shared DataStore.
"""

from __future__ import annotations

from .exceptions import CrewMemberNotFoundError, ValidationError
from .registration import get_member
from .store import DataStore


def _normalize_role(role: str) -> str:
    return role.strip().lower()


def assign_role(store: DataStore, member_name: str, role: str) -> None:
    """Assign an additional role to an existing crew member."""
    if role is None or not str(role).strip():
        raise ValidationError("Role must be non-empty")

    member = get_member(store, member_name)  # raises CrewMemberNotFoundError
    role_key = _normalize_role(str(role))

    store.crew_roles.setdefault(member.name, set()).add(role_key)


def set_skill(store: DataStore, member_name: str, role: str, level: int) -> None:
    """Set a crew member's skill level for a specific role."""
    if role is None or not str(role).strip():
        raise ValidationError("Role must be non-empty")
    if not isinstance(level, int):
        raise ValidationError("Skill level must be an integer")
    if level < 0 or level > 10:
        raise ValidationError("Skill level must be in range 0..10")

    member = get_member(store, member_name)  # raises CrewMemberNotFoundError
    role_key = _normalize_role(str(role))

    # Ensure the role is tracked before setting a skill for it.
    store.crew_roles.setdefault(member.name, set()).add(role_key)
    store.crew_skills.setdefault(member.name, {})[role_key] = level


def has_role(store: DataStore, member_name: str, role: str) -> bool:
    """Return True if the member has the given role (including their registered role)."""
    if role is None or not str(role).strip():
        raise ValidationError("Role must be non-empty")

    member = get_member(store, member_name)  # raises CrewMemberNotFoundError
    role_key = _normalize_role(str(role))

    registered_role = _normalize_role(member.role)
    if role_key == registered_role:
        return True

    extra_roles = store.crew_roles.get(member.name, set())
    return role_key in extra_roles


def get_skill(store: DataStore, member_name: str, role: str, *, default: int | None = None) -> int | None:
    """Return the member's skill for role, or default if not set."""
    if role is None or not str(role).strip():
        raise ValidationError("Role must be non-empty")

    member = get_member(store, member_name)  # raises CrewMemberNotFoundError
    role_key = _normalize_role(str(role))
    return store.crew_skills.get(member.name, {}).get(role_key, default)


def list_members_with_role(store: DataStore, role: str) -> list[str]:
    """Return a list of member names that currently have `role`."""
    if role is None or not str(role).strip():
        raise ValidationError("Role must be non-empty")

    role_key = _normalize_role(str(role))
    result: list[str] = []

    for member in store.crew.values():
        if role_key == _normalize_role(member.role):
            result.append(member.name)
            continue
        extra_roles = store.crew_roles.get(member.name, set())
        if role_key in extra_roles:
            result.append(member.name)

    return result
