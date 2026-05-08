from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    joined_at = models.DateTimeField(default=timezone.now)
    two_fa_enabled = models.BooleanField(default=False)
    is_kyc_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.username[:2].upper()

    @property
    def pending_payout(self):
        from apps.letters.models import Letter
        from django.conf import settings

        count = Letter.objects.filter(
            user=self, status=Letter.Status.APPROVED, payout_credited=False
        ).count()
        return count * getattr(settings, "LETTER_APPROVAL_PAYMENT", 99.50)


class Kyc(models.Model):
    STATUS_CHOICES = (
        ("processing", "Processing"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    )

    user = models.OneToOneField(User, related_name="user_kyc", on_delete=models.CASCADE)
    document_front = models.ImageField(upload_to="document")
    document_back = models.ImageField(upload_to="document")
    is_approved = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="processing"
    )

    def __str__(self):
        return f"{self.user.username} KYC"
