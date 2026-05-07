from django.db import models
from django.conf import settings
from django.utils import timezone


class Letter(models.Model):

    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        APPROVED = 'approved', 'Approved'
        DECLINED = 'declined', 'Declined'

    class Category(models.TextChoices):
        BUSINESS   = 'business',   'Business'
        COVER      = 'cover',      'Cover Letter'
        COMPLAINT  = 'complaint',  'Complaint'
        GRANT      = 'grant',      'Grant Application'
        LEGAL      = 'legal',      'Legal'
        INVESTMENT = 'investment', 'Investment Pitch'
        PERSONAL   = 'personal',   'Personal'
        OTHER      = 'other',      'Other'

    user                 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='letters')
    title                = models.CharField(max_length=200)
    category             = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    body                 = models.TextField()
    recipient_name       = models.CharField(max_length=200, blank=True)
    recipient_organization = models.CharField(max_length=200, blank=True)
    status               = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    admin_note           = models.TextField(blank=True, help_text="Reason for approval/decline (shown to user)")
    earnings             = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    payout_credited      = models.BooleanField(default=False)
    submitted_at         = models.DateTimeField(default=timezone.now)
    reviewed_at          = models.DateTimeField(null=True, blank=True)
    word_count           = models.PositiveIntegerField(default=0)

    class Meta:
        ordering     = ['-submitted_at']
        verbose_name = 'Letter'
        verbose_name_plural = 'Letters'

    def __str__(self):
        return f"#{self.pk} – {self.title} ({self.user})"

    @property
    def letter_id(self):
        return f"LT-{self.pk:04d}"

    def save(self, *args, **kwargs):
        self.word_count = len(self.body.split())
        super().save(*args, **kwargs)
