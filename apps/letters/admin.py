from django.contrib import admin
from django.utils import timezone
from django.conf import settings
from .models import Letter


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display    = ('letter_id', 'title', 'user', 'category', 'status', 'earnings', 'submitted_at')
    list_filter     = ('status', 'category')
    search_fields   = ('title', 'user__username', 'user__email')
    readonly_fields = ('submitted_at', 'word_count', 'earnings', 'payout_credited')
    actions         = ['approve_letters', 'decline_letters']

    fieldsets = (
        ('Letter Info',  {'fields': ('user', 'title', 'category', 'body', 'word_count', 'recipient_name', 'recipient_organization')}),
        ('Review',       {'fields': ('status', 'admin_note', 'reviewed_at')}),
        ('Financials',   {'fields': ('earnings', 'payout_credited')}),
    )

    def approve_letters(self, request, queryset):
        payment = getattr(settings, 'LETTER_APPROVAL_PAYMENT', 25.00)
        approved = 0
        for letter in queryset.filter(status='pending'):
            letter.status         = Letter.Status.APPROVED
            letter.earnings       = payment
            letter.reviewed_at    = timezone.now()
            letter.payout_credited = True
            letter.save()
            user              = letter.user
            user.balance     += payment
            user.total_earned += payment
            user.save()
            approved += 1
        self.message_user(request, f"{approved} letter(s) approved and ${approved * payment:.2f} credited.")
    approve_letters.short_description = "✅ Approve selected letters & credit payment"

    def decline_letters(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='declined', reviewed_at=timezone.now()
        )
        self.message_user(request, f"{updated} letter(s) declined.")
    decline_letters.short_description = "❌ Decline selected letters"
