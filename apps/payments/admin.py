from django.contrib import admin
from django.utils import timezone
from .models import Deposit, Withdrawal


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display  = ('user', 'method', 'amount_usd', 'tx_hash', 'status', 'created_at')
    list_filter   = ('status', 'method')
    search_fields = ('user__username', 'tx_hash')
    actions       = ['confirm_deposits', 'fail_deposits']

    def confirm_deposits(self, request, queryset):
        for deposit in queryset.filter(status='pending'):
            deposit.status       = 'confirmed'
            deposit.confirmed_at = timezone.now()
            deposit.save()
            user          = deposit.user
            user.balance += deposit.amount_usd
            user.save()
        self.message_user(request, "Selected deposits confirmed and balances credited.")
    confirm_deposits.short_description = "✅ Confirm deposits & credit balances"

    def fail_deposits(self, request, queryset):
        queryset.filter(status='pending').update(status='failed')
        self.message_user(request, "Selected deposits marked as failed.")
    fail_deposits.short_description = "❌ Mark as failed"


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display  = ('user', 'amount', 'bank_name', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('user__username', 'bank_name', 'account_number')
    actions       = ['complete_withdrawals', 'reject_withdrawals']

    def complete_withdrawals(self, request, queryset):
        queryset.filter(status__in=['pending', 'processing']).update(
            status='completed', processed_at=timezone.now()
        )
        self.message_user(request, "Selected withdrawals marked as completed.")
    complete_withdrawals.short_description = "✅ Mark as completed"

    def reject_withdrawals(self, request, queryset):
        for w in queryset.filter(status__in=['pending', 'processing']):
            w.status       = 'rejected'
            w.processed_at = timezone.now()
            w.save()
            w.user.balance += w.amount
            w.user.save()
        self.message_user(request, "Withdrawals rejected and balances refunded.")
    reject_withdrawals.short_description = "❌ Reject & refund balance"
