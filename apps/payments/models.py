from django.db import models
from django.conf import settings
from django.utils import timezone


class Deposit(models.Model):
    class Method(models.TextChoices):
        BTC  = 'BTC',  'Bitcoin (BTC)'
        USDT = 'USDT', 'Tether (USDT TRC-20)'
        ETH  = 'ETH',  'Ethereum (ETH)'

    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending Confirmation'
        CONFIRMED = 'confirmed', 'Confirmed'
        FAILED    = 'failed',    'Failed'

    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deposits')
    method         = models.CharField(max_length=10, choices=Method.choices)
    amount_usd     = models.DecimalField(max_digits=12, decimal_places=2)
    tx_hash        = models.CharField(max_length=200, blank=True)
    wallet_address = models.CharField(max_length=200, blank=True)
    status         = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at     = models.DateTimeField(default=timezone.now)
    confirmed_at   = models.DateTimeField(null=True, blank=True)
    admin_note     = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | {self.method} | ${self.amount_usd} | {self.status}"

    def get_status_display_pill(self):
        return self.status


class Withdrawal(models.Model):
    class Status(models.TextChoices):
        PENDING    = 'pending',    'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED  = 'completed',  'Completed'
        REJECTED   = 'rejected',   'Rejected'

    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name      = models.CharField(max_length=200)
    account_name   = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50, blank=True)
    swift_code     = models.CharField(max_length=20, blank=True)
    status         = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at     = models.DateTimeField(default=timezone.now)
    processed_at   = models.DateTimeField(null=True, blank=True)
    admin_note     = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | ${self.amount} | {self.status}"
