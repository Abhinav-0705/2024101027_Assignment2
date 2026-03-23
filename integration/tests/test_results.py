import pytest

from integration.code.streetrace_manager.exceptions import ResultError, ValidationError
from integration.code.streetrace_manager.inventory import add_vehicle, get_cash_balance, get_vehicle
from integration.code.streetrace_manager.race_management import create_race, enter_race
from integration.code.streetrace_manager.registration import register_member
from integration.code.streetrace_manager.results import get_rankings, get_result, record_race_result
from integration.code.streetrace_manager.store import DataStore


class TestResults:
    def setup_method(self):
        self.store = DataStore()
        register_member(self.store, "Alice", "driver")
        register_member(self.store, "Dana", "driver")
        add_vehicle(self.store, "CAR1", "Nissan")
        add_vehicle(self.store, "CAR2", "Toyota")

        self.race = create_race(self.store, "Downtown Dash")
        enter_race(self.store, self.race.race_id, "Alice", "CAR1")
        enter_race(self.store, self.race.race_id, "Dana", "CAR2")

    def test_record_result_updates_cash_and_rankings(self):
        assert get_cash_balance(self.store) == 0
        res = record_race_result(self.store, self.race.race_id, winner_driver="Alice", prize_money=500)
        assert res.winner_driver == "Alice"
        assert get_cash_balance(self.store) == 500

        rankings = get_rankings(self.store)
        assert rankings[0] == ("Alice", 1)

    def test_record_result_requires_winner_in_entries(self):
        with pytest.raises(ResultError):
            record_race_result(self.store, self.race.race_id, winner_driver="Bob", prize_money=100)

    def test_record_result_rejects_negative_prize(self):
        with pytest.raises(ValidationError):
            record_race_result(self.store, self.race.race_id, winner_driver="Alice", prize_money=-1)

    def test_record_result_only_once(self):
        record_race_result(self.store, self.race.race_id, winner_driver="Alice", prize_money=10)
        with pytest.raises(ResultError):
            record_race_result(self.store, self.race.race_id, winner_driver="Alice", prize_money=10)

    def test_record_result_can_mark_vehicle_damaged(self):
        record_race_result(
            self.store,
            self.race.race_id,
            winner_driver="Dana",
            prize_money=200,
            damaged_vehicle_id="CAR1",
        )
        assert get_vehicle(self.store, "CAR1").condition == "damaged"

    def test_get_result_missing_raises(self):
        with pytest.raises(ResultError):
            get_result(self.store, "999")
