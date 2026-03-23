import pytest

from integration.code.streetrace_manager.exceptions import (
    DuplicateVehicleError,
    ValidationError,
    VehicleNotFoundError,
)
from integration.code.streetrace_manager.inventory import (
    add_cash,
    add_part,
    add_tool,
    add_vehicle,
    deduct_cash,
    get_cash_balance,
    get_part_qty,
    get_tool_qty,
    get_vehicle,
    list_vehicles,
    mark_vehicle_damaged,
)
from integration.code.streetrace_manager.store import DataStore


class TestInventory:
    def setup_method(self):
        self.store = DataStore()

    def test_cash_add_and_deduct_happy_path(self):
        assert get_cash_balance(self.store) == 0
        add_cash(self.store, 500)
        assert get_cash_balance(self.store) == 500
        deduct_cash(self.store, 200)
        assert get_cash_balance(self.store) == 300

    def test_deduct_cash_rejects_insufficient_funds(self):
        add_cash(self.store, 50)
        with pytest.raises(ValidationError):
            deduct_cash(self.store, 51)

    def test_cash_rejects_negative_amounts(self):
        with pytest.raises(ValidationError):
            add_cash(self.store, -1)
        with pytest.raises(ValidationError):
            deduct_cash(self.store, -1)

    def test_add_vehicle_and_lookup(self):
        v = add_vehicle(self.store, "CAR1", "Nissan")
        assert v.vehicle_id == "CAR1"
        assert v.condition == "ok"
        looked = get_vehicle(self.store, "CAR1")
        assert looked == v
        assert len(list_vehicles(self.store)) == 1

    def test_add_vehicle_duplicate_rejected(self):
        add_vehicle(self.store, "CAR1", "Nissan")
        with pytest.raises(DuplicateVehicleError):
            add_vehicle(self.store, "CAR1", "Toyota")

    def test_get_vehicle_missing_raises(self):
        with pytest.raises(VehicleNotFoundError):
            get_vehicle(self.store, "MISSING")

    def test_mark_vehicle_damaged_creates_damaged_state(self):
        add_vehicle(self.store, "CAR1", "Nissan")
        damaged = mark_vehicle_damaged(self.store, "CAR1")
        assert damaged.condition == "damaged"
        assert get_vehicle(self.store, "CAR1").condition == "damaged"

    def test_parts_and_tools_quantities(self):
        assert get_part_qty(self.store, "engine") == 0
        add_part(self.store, "engine", 2)
        add_part(self.store, "ENGINE", 1)
        assert get_part_qty(self.store, "engine") == 3

        assert get_tool_qty(self.store, "jack") == 0
        add_tool(self.store, "jack", 1)
        assert get_tool_qty(self.store, "jack") == 1

    def test_parts_tools_reject_invalid(self):
        with pytest.raises(ValidationError):
            add_part(self.store, "", 1)
        with pytest.raises(ValidationError):
            add_tool(self.store, "wrench", -1)
