from django.db import models


class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True, help_text="e.g. LOS, ABV, JFK")
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default="UTC", help_text="e.g. Africa/Lagos")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.iata_code} — {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        self.iata_code = self.iata_code.upper()
        super().save(*args, **kwargs)