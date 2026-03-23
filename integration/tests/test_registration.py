"""Unit tests for StreetRace Manager registration module."""

import pytest

from integration.code.streetrace_manager.exceptions import (
    CrewMemberNotFoundError,
    DuplicateCrewMemberError,
    ValidationError,
)
from integration.code.streetrace_manager.registration import (
    get_member,
    list_members,
    register_member,
)
from integration.code.streetrace_manager.store import DataStore


def test_register_member_happy_path_returns_member_and_stores_it():
    store = DataStore()
    member = register_member(store, "Mia", "driver")
    assert member.name == "Mia"
    assert member.role == "driver"

    looked_up = get_member(store, "mia")
    assert looked_up == member


def test_register_member_rejects_duplicate_names_case_insensitive():
    store = DataStore()
    register_member(store, "Mia", "driver")
    with pytest.raises(DuplicateCrewMemberError):
        register_member(store, "mia", "mechanic")


def test_register_member_rejects_empty_name():
    store = DataStore()
    with pytest.raises(ValidationError):
        register_member(store, "   ", "driver")


def test_register_member_rejects_empty_role():
    store = DataStore()
    with pytest.raises(ValidationError):
        register_member(store, "Mia", "")


def test_get_member_raises_when_not_found():
    store = DataStore()
    with pytest.raises(CrewMemberNotFoundError):
        get_member(store, "unknown")


def test_list_members_returns_all_in_registration_order():
    store = DataStore()
    register_member(store, "A", "driver")
    register_member(store, "B", "mechanic")
    assert [m.name for m in list_members(store)] == ["A", "B"]
