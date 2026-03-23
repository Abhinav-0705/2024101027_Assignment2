import pytest

from integration.code.streetrace_manager.crew_management import (
    assign_role,
    get_skill,
    has_role,
    list_members_with_role,
    set_skill,
)
from integration.code.streetrace_manager.exceptions import CrewMemberNotFoundError, ValidationError
from integration.code.streetrace_manager.registration import register_member
from integration.code.streetrace_manager.store import DataStore


class TestCrewManagement:
    def setup_method(self):
        self.store = DataStore()
        register_member(self.store, "Alice", "driver")
        register_member(self.store, "Bob", "mechanic")

    def test_has_role_true_for_registered_role(self):
        assert has_role(self.store, "Alice", "driver") is True

    def test_assign_role_adds_extra_role(self):
        assert has_role(self.store, "Alice", "strategist") is False
        assign_role(self.store, "Alice", "strategist")
        assert has_role(self.store, "Alice", "strategist") is True

    def test_assign_role_requires_registered_member(self):
        with pytest.raises(CrewMemberNotFoundError):
            assign_role(self.store, "Charlie", "driver")

    def test_set_skill_validates_level_range(self):
        with pytest.raises(ValidationError):
            set_skill(self.store, "Alice", "driver", -1)
        with pytest.raises(ValidationError):
            set_skill(self.store, "Alice", "driver", 11)

    def test_set_skill_requires_int(self):
        with pytest.raises(ValidationError):
            set_skill(self.store, "Alice", "driver", 7.5)  # type: ignore[arg-type]

    def test_set_skill_sets_and_gets(self):
        assert get_skill(self.store, "Alice", "driver") is None
        set_skill(self.store, "Alice", "driver", 7)
        assert get_skill(self.store, "Alice", "driver") == 7

    def test_set_skill_implies_role_assignment(self):
        assert has_role(self.store, "Alice", "strategist") is False
        set_skill(self.store, "Alice", "strategist", 5)
        assert has_role(self.store, "Alice", "strategist") is True
        assert get_skill(self.store, "Alice", "strategist") == 5

    def test_list_members_with_role_includes_registered_and_extra(self):
        assign_role(self.store, "Bob", "driver")
        drivers = list_members_with_role(self.store, "driver")
        assert set(drivers) == {"Alice", "Bob"}

    def test_role_validation_non_empty(self):
        with pytest.raises(ValidationError):
            assign_role(self.store, "Alice", "")
        with pytest.raises(ValidationError):
            has_role(self.store, "Alice", " ")
