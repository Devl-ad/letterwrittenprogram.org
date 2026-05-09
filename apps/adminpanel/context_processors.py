from apps.letters.models import Letter
from apps.payments.models import Deposit, Withdrawal
from apps.accounts.models import Kyc


def admin_counts(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    try:

        pending_kyc = Kyc.objects.filter(status="processing").count()
    except Exception:
        pending_kyc = 0
    return {
        "pending_letters_count": Letter.objects.filter(status="pending").count(),
        "pending_deposits_count": Deposit.objects.filter(status="pending").count(),
        "pending_withdrawals_count": Withdrawal.objects.filter(
            status="pending"
        ).count(),
        "pending_kyc_count": pending_kyc,
    }
