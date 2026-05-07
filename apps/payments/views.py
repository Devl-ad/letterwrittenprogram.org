from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import DepositForm, WithdrawalForm
from .models import Deposit, Withdrawal

CRYPTO_WALLETS = {
    "BTC": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "USDT": "TN3W4T6gNgLkEVfGqRDRYdvKJCDTrHNDHR",
    "ETH": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
}


@login_required
def deposit_view(request):
    form = DepositForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        deposit = form.save(commit=False)
        deposit.user = request.user
        deposit.wallet_address = CRYPTO_WALLETS.get(deposit.method, "")
        deposit.save()
        messages.success(
            request,
            f"Deposit request of ${deposit.amount_usd} submitted! "
            f"We'll confirm your {deposit.method} transaction within 1–24 hours.",
        )
        return redirect("payments:deposit")

    recent_deposits = Deposit.objects.filter(user=request.user)[:5]
    return render(
        request,
        "dashboard/deposit.html",
        {
            "form": form,
            "wallets": CRYPTO_WALLETS,
            "recent_deposits": recent_deposits,
        },
    )


@login_required
def withdrawal_view(request):
    form = WithdrawalForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        withdrawal = form.save(commit=False)
        withdrawal.user = request.user
        request.user.balance -= withdrawal.amount
        request.user.save()
        withdrawal.save()
        messages.success(
            request,
            f"Withdrawal request of ${withdrawal.amount} submitted. "
            f"Processing takes 1–3 business days.",
        )
        return redirect("payments:withdrawal")

    recent_withdrawals = Withdrawal.objects.filter(user=request.user)[:5]
    return render(
        request,
        "dashboard/withdrawal.html",
        {
            "form": form,
            "recent_withdrawals": recent_withdrawals,
        },
    )


@login_required
def transactions_view(request):
    deposits = Deposit.objects.filter(user=request.user)
    withdrawals = Withdrawal.objects.filter(user=request.user)

    txns = []
    for d in deposits:
        txns.append(
            {
                "type": "deposit",
                "amount": d.amount_usd,
                "method": d.method,
                "status": d.status,
                "date": d.created_at,
                "note": d.tx_hash or "—",
            }
        )
    for w in withdrawals:
        txns.append(
            {
                "type": "withdrawal",
                "amount": w.amount,
                "method": "Bank Transfer",
                "status": w.status,
                "date": w.created_at,
                "note": w.bank_name,
            }
        )

    txns.sort(key=lambda x: x["date"], reverse=True)
    return render(request, "dashboard/transactions.html", {"txns": txns})
