from apps.letters.models import Letter
from apps.payments.models import Deposit, Withdrawal


def admin_counts(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    return {
        'pending_letters_count':    Letter.objects.filter(status='pending').count(),
        'pending_deposits_count':   Deposit.objects.filter(status='pending').count(),
        'pending_withdrawals_count': Withdrawal.objects.filter(status='pending').count(),
    }
