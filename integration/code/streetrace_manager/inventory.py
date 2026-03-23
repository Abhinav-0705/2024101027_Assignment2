"""Inventory module.

Responsibilities:
- Track cash balance
- Track vehicles (cars)
- Track spare parts and tools

Business rules:
- Cash balance cannot go negative.
- Quantities for parts/tools cannot be negative.
- Vehicle IDs must be unique.
"""

from __future__ import annotations

from .exceptions import DuplicateVehicleError, ValidationError, VehicleNotFoundError
from .models import Vehicle
from .store import DataStore


def add_cash(store: DataStore, amount: int) -> int:
    """Increase cash balance by `amount` and return the new balance."""
    if not isinstance(amount, int):
        raise ValidationError("Cash amount must be an integer")
    if amount < 0:
        raise ValidationError("Cash amount must be non-negative")
    store.cash_balance += amount
    return store.cash_balance


def deduct_cash(store: DataStore, amount: int) -> int:
    """Decrease cash balance by `amount` and return the new balance."""
    if not isinstance(amount, int):
        raise ValidationError("Cash amount must be an integer")
    if amount < 0:
        raise ValidationError("Cash amount must be non-negative")
    if store.cash_balance - amount < 0:
        raise ValidationError("Insufficient cash balance")
    store.cash_balance -= amount
    return store.cash_balance


def get_cash_balance(store: DataStore) -> int:
    return store.cash_balance


def add_vehicle(store: DataStore, vehicle_id: str, model: str) -> Vehicle:
    if vehicle_id is None or not str(vehicle_id).strip():
        raise ValidationError("Vehicle ID must be non-empty")
    if model is None or not str(model).strip():
        raise ValidationError("Vehicle model must be non-empty")

    vid = str(vehicle_id).strip()
    if vid in store.vehicles:
        raise DuplicateVehicleError(f"Vehicle '{vid}' already exists")

    vehicle = Vehicle(vehicle_id=vid, model=str(model).strip(), condition="ok")
    store.vehicles[vid] = vehicle
    return vehicle


def get_vehicle(store: DataStore, vehicle_id: str) -> Vehicle:
    vid = str(vehicle_id).strip()
    vehicle = store.vehicles.get(vid)
    if vehicle is None:
        raise VehicleNotFoundError(f"Vehicle '{vid}' not found")
    return vehicle


def list_vehicles(store: DataStore) -> list[Vehicle]:
    return list(store.vehicles.values())


def mark_vehicle_damaged(store: DataStore, vehicle_id: str) -> Vehicle:
    vehicle = get_vehicle(store, vehicle_id)
    damaged = Vehicle(vehicle_id=vehicle.vehicle_id, model=vehicle.model, condition="damaged")
    store.vehicles[vehicle.vehicle_id] = damaged
    return damaged


def add_part(store: DataStore, name: str, qty: int) -> int:
    return _add_item(store.parts, name, qty, item_label="part")


def add_tool(store: DataStore, name: str, qty: int) -> int:
    return _add_item(store.tools, name, qty, item_label="tool")


def get_part_qty(store: DataStore, name: str) -> int:
    return store.parts.get(str(name).strip().lower(), 0)


def get_tool_qty(store: DataStore, name: str) -> int:
    return store.tools.get(str(name).strip().lower(), 0)


def _add_item(bucket: dict[str, int], name: str, qty: int, *, item_label: str) -> int:
    if name is None or not str(name).strip():
        raise ValidationError(f"{item_label.title()} name must be non-empty")
    if not isinstance(qty, int):
        raise ValidationError(f"{item_label.title()} quantity must be an integer")
    if qty < 0:
        raise ValidationError(f"{item_label.title()} quantity must be non-negative")

    key = str(name).strip().lower()
    bucket[key] = bucket.get(key, 0) + qty
    return bucket[key]
