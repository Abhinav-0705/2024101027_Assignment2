import pytest

from integration.code.streetrace_manager.exceptions import (
    CrewMemberNotFoundError,
    RaceEntryError,
    RaceNotFoundError,
    ValidationError,
)
from integration.code.streetrace_manager.inventory import add_vehicle, mark_vehicle_damaged
from integration.code.streetrace_manager.race_management import create_race, enter_race, get_race
from integration.code.streetrace_manager.registration import register_member
from integration.code.streetrace_manager.store import DataStore


class TestRaceManagement:
    def setup_method(self):
        self.store = DataStore()
        register_member(self.store, "Alice", "driver")
        register_member(self.store, "Bob", "mechanic")
        add_vehicle(self.store, "CAR1", "Nissan")
        add_vehicle(self.store, "CAR2", "Toyota")

    def test_create_race_requires_name(self):
        with pytest.raises(ValidationError):
            create_race(self.store, " ")

    def test_create_and_get_race(self):
        race = create_race(self.store, "Downtown Dash")
        looked = get_race(self.store, race.race_id)
        assert looked.race_id == race.race_id

    def test_get_race_missing_raises(self):
        with pytest.raises(RaceNotFoundError):
            get_race(self.store, "999")

    def test_enter_race_happy_path(self):
        race = create_race(self.store, "Downtown Dash")
        entry = enter_race(self.store, race.race_id, "Alice", "CAR1")
        assert entry.driver_name == "Alice"
        assert entry.vehicle_id == "CAR1"
        assert len(get_race(self.store, race.race_id).entries) == 1

    def test_enter_race_rejects_non_driver(self):
        race = create_race(self.store, "Downtown Dash")
        with pytest.raises(RaceEntryError):
            enter_race(self.store, race.race_id, "Bob", "CAR1")

    def test_enter_race_requires_registered_driver(self):
        race = create_race(self.store, "Downtown Dash")
        with pytest.raises(CrewMemberNotFoundError):
            enter_race(self.store, race.race_id, "Charlie", "CAR1")

    def test_enter_race_rejects_missing_vehicle(self):
        race = create_race(self.store, "Downtown Dash")
        with pytest.raises(Exception):
            # inventory raises VehicleNotFoundError, but race module doesn't wrap it
            enter_race(self.store, race.race_id, "Alice", "MISSING")

    def test_enter_race_rejects_damaged_vehicle(self):
        race = create_race(self.store, "Downtown Dash")
        mark_vehicle_damaged(self.store, "CAR1")
        with pytest.raises(RaceEntryError):
            enter_race(self.store, race.race_id, "Alice", "CAR1")

    def test_enter_race_rejects_duplicate_driver(self):
        race = create_race(self.store, "Downtown Dash")
        enter_race(self.store, race.race_id, "Alice", "CAR1")
        with pytest.raises(RaceEntryError):
            enter_race(self.store, race.race_id, "Alice", "CAR2")

    def test_enter_race_rejects_duplicate_vehicle(self):
        race = create_race(self.store, "Downtown Dash")
        register_member(self.store, "Dana", "driver")
        enter_race(self.store, race.race_id, "Alice", "CAR1")
        with pytest.raises(RaceEntryError):
            enter_race(self.store, race.race_id, "Dana", "CAR1")
