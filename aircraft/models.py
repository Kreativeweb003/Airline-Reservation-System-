from django.db import models


class Aircraft(models.Model):
    class Manufacturer(models.TextChoices):
        BOEING = "BOEING", "Boeing"
        AIRBUS = "AIRBUS", "Airbus"
        EMBRAER = "EMBRAER", "Embraer"
        BOMBARDIER = "BOMBARDIER", "Bombardier"
        OTHER = "OTHER", "Other"

    model_name = models.CharField(max_length=100, help_text="e.g. 737-800, A320neo")
    manufacturer = models.CharField(max_length=20, choices=Manufacturer.choices, default=Manufacturer.OTHER)
    registration_number = models.CharField(max_length=20, unique=True, help_text="Tail number, e.g. 5N-ABC")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["manufacturer", "model_name"]

    def __str__(self):
        return f"{self.manufacturer} {self.model_name} ({self.registration_number})"

    @property
    def total_capacity(self):
        return sum(cfg.seat_count for cfg in self.seat_configurations.all())


class SeatConfiguration(models.Model):
    class SeatClass(models.TextChoices):
        ECONOMY = "ECONOMY", "Economy"
        BUSINESS = "BUSINESS", "Business"
        FIRST = "FIRST", "First Class"

    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="seat_configurations")
    seat_class = models.CharField(max_length=20, choices=SeatClass.choices)
    row_start = models.PositiveIntegerField()
    row_end = models.PositiveIntegerField()
    columns = models.CharField(max_length=10, help_text="e.g. ABCDEF (one letter per seat column)")

    class Meta:
        ordering = ["row_start"]
        constraints = [
            models.UniqueConstraint(
                fields=["aircraft", "seat_class"], name="unique_class_per_aircraft"
            )
        ]

    def __str__(self):
        return f"{self.aircraft.registration_number} — {self.seat_class} (rows {self.row_start}-{self.row_end})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.row_end < self.row_start:
            raise ValidationError("row_end must be greater than or equal to row_start.")
        if not self.columns or not self.columns.isalpha():
            raise ValidationError("Columns must be letters only, e.g. ABCDEF.")

    @property
    def row_count(self):
        return self.row_end - self.row_start + 1

    @property
    def seat_count(self):
        return self.row_count * len(self.columns)

    def generate_seat_labels(self):
        """Returns list of (row, column, seat_class) tuples, e.g. (12, 'A', 'ECONOMY')."""
        labels = []
        for row in range(self.row_start, self.row_end + 1):
            for col in self.columns:
                labels.append((row, col, self.seat_class))
        return labels




