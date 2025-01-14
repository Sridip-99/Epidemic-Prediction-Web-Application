from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check if the OTP has expired (1-minute validity)."""
        expiry_time = self.created_at + timedelta(minutes=1)
        return now() > expiry_time

    def __str__(self):
        return f"OTP for {self.email}"

class TemporaryUser(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    doctor_id = models.CharField(max_length=10, default="0")  # Set default to "0"
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check if the temporary user has expired (1-minute validity)."""
        expiry_time = self.created_at + timedelta(minutes=1)
        return now() > expiry_time

    def __str__(self):
        return f"Temporary User: {self.email}"
