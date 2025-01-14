from django.core.management.base import BaseCommand
from signup_app.models import OTP
from django.utils.timezone import now
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete expired OTPs'

    def handle(self, *args, **kwargs):
        expired_otps = OTP.objects.filter(created_at__lt=now() - timedelta(minutes=10))
        expired_otps.delete()
        self.stdout.write(f"Deleted {expired_otps.count()} expired OTP(s).")
