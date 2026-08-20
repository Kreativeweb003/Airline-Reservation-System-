from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Aircraft, SeatConfiguration


def validate_no_row_overlap(aircraft: Aircraft, configs: list[SeatConfiguration]):
    """Ensures seat classes on the same aircraft don't share row numbers."""
    occupied_rows = set()
    for cfg in configs:
        rows = set(range(cfg.row_start, cfg.row_end + 1))
        if rows & occupied_rows:
            raise ValidationError(
                f"Row overlap detected involving {cfg.seat_class} (rows {cfg.row_start}-{cfg.row_end})."
            )
        occupied_rows |= rows


@transaction.atomic
def create_aircraft_with_seating(*, model_name, manufacturer, registration_number, seat_configs: list[dict]):
    """
    seat_configs: list of dicts like
        {"seat_class": "ECONOMY", "row_start": 9, "row_end": 30, "columns": "ABCDEF"}
    """
    if Aircraft.objects.filter(registration_number=registration_number).exists():
        raise ValidationError(f"Aircraft with registration {registration_number} already exists.")

    aircraft = Aircraft.objects.create(
        model_name=model_name,
        manufacturer=manufacturer,
        registration_number=registration_number,
    )

    configs = [SeatConfiguration(aircraft=aircraft, **cfg) for cfg in seat_configs]
    validate_no_row_overlap(aircraft, configs)

    for cfg in configs:
        cfg.full_clean()
        cfg.save()

    return aircraft


def deactivate_aircraft(aircraft: Aircraft):
    aircraft.is_active = False
    aircraft.save(update_fields=["is_active"])