"""Custom exceptions for StreetRace Manager."""


class StreetRaceError(Exception):
    """Base exception for StreetRace Manager."""


class DuplicateCrewMemberError(StreetRaceError):
    """Raised when attempting to register a crew member that already exists."""


class CrewMemberNotFoundError(StreetRaceError):
    """Raised when a requested crew member cannot be found."""


class ValidationError(StreetRaceError):
    """Raised when input data fails validation."""


class DuplicateVehicleError(StreetRaceError):
    """Raised when attempting to add a vehicle that already exists."""


class VehicleNotFoundError(StreetRaceError):
    """Raised when a requested vehicle cannot be found."""


class RaceNotFoundError(StreetRaceError):
    """Raised when a requested race cannot be found."""


class RaceEntryError(StreetRaceError):
    """Raised when a race entry violates business rules."""
