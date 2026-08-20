from django.core.exceptions import ValidationError
from .models import Airport


def create_airport(*, iata_code, name, city, country, timezone="UTC"):
    iata_code = iata_code.upper().strip()
    if Airport.objects.filter(iata_code=iata_code).exists():
        raise ValidationError(f"Airport with code {iata_code} already exists.")
    return Airport.objects.create(
        iata_code=iata_code, name=name, city=city, country=country, timezone=timezone,
    )


def deactivate_airport(airport: Airport):
    """Soft delete — used instead of hard delete since routes/flights may reference it."""
    airport.is_active = False
    airport.save(update_fields=["is_active"])


def search_airports(query: str):
    if not query:
        return Airport.objects.filter(is_active=True)
    return Airport.objects.filter(is_active=True).filter(
        models_q(query)
    )


def models_q(query):
    from django.db.models import Q
    return (
        Q(iata_code__icontains=query)
        | Q(city__icontains=query)
        | Q(name__icontains=query)
        | Q(country__icontains=query)
    )