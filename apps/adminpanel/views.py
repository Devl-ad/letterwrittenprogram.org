import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.accounts.models import User
from apps.letters.models import Letter
from apps.payments.models import Deposit, Withdrawal
from decimal import Decimal

is_admin = user_passes_test(lambda u: u.is_staff, login_url="login")


def admin_required(view_func):
    return login_required(is_admin(view_func))


# ── helpers ──────────────────────────────────────────────
def _send_letter_email(letter, status, note=""):
    subject_map = {
        "approved": f'✅ Your letter "{letter.title}" has been approved!',
        "declined": f'❌ Your letter "{letter.title}" was not approved',
    }
    body_map = {
        "approved": (
            f"Hi {letter.user.first_name or letter.user.username},\n\n"
            f'Great news! Your letter "{letter.title}" (#{letter.letter_id}) '
            f"has been approved and ${letter.earnings:.2f} has been credited to your balance.\n\n"
            f"{'Admin note: ' + note + chr(10) + chr(10) if note else ''}"
            f"Log in to view your balance and request a withdrawal.\n\n"
            f"— Smart Writing Finance Team"
        ),
        "declined": (
            f"Hi {letter.user.first_name or letter.user.username},\n\n"
            f'Unfortunately your letter "{letter.title}" (#{letter.letter_id}) '
            f"was not approved at this time.\n\n"
            f"{'Reason: ' + note + chr(10) + chr(10) if note else ''}"
            f"You're welcome to submit a revised version.\n\n"
            f"— Smart Writing Finance Team"
        ),
    }
    try:
        send_mail(
            subject=subject_map[status],
            message=body_map[status],
            from_email=getattr(
                settings, "DEFAULT_FROM_EMAIL", "noreply@smartwritingfinance.com"
            ),
            recipient_list=[letter.user.email],
            fail_silently=True,
        )
    except Exception:
        pass


# ── Dashboard ─────────────────────────────────────────────
@admin_required
def admin_dashboard(request):
    today = datetime.date.today()
    letters = Letter.objects.all()
    users = User.objects.filter(is_staff=False)

    stats = {
        "total_users": users.count(),
        "new_users_today": users.filter(date_joined__date=today).count(),
        "total_letters": letters.count(),
        "pending_letters": letters.filter(status="pending").count(),
        "approved_letters": letters.filter(status="approved").count(),
        "declined_letters": letters.filter(status="declined").count(),
        "total_paid_out": letters.filter(status="approved").aggregate(
            t=Sum("earnings")
        )["t"]
        or 0,
        "pending_deposits": Deposit.objects.filter(status="pending").count(),
        "pending_withdrawals": Withdrawal.objects.filter(status="pending").count(),
    }

    recent_letters = letters.filter(status="pending").order_by("-submitted_at")[:8]
    recent_users = users.order_by("-date_joined")[:5]
    recent_deposits = Deposit.objects.filter(status="pending").order_by("-created_at")[
        :5
    ]

    return render(
        request,
        "adminpanel/dashboard.html",
        {
            "stats": stats,
            "recent_letters": recent_letters,
            "recent_users": recent_users,
            "recent_deposits": recent_deposits,
        },
    )


# ── Letters ───────────────────────────────────────────────
@admin_required
def admin_letters(request):
    qs = Letter.objects.select_related("user").all()
    status = request.GET.get("status", "")
    search = request.GET.get("q", "")
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__email__icontains=search)
        )

    paginator = Paginator(qs, 15)
    letters = paginator.get_page(request.GET.get("page", 1))

    counts = {
        "all": Letter.objects.count(),
        "pending": Letter.objects.filter(status="pending").count(),
        "approved": Letter.objects.filter(status="approved").count(),
        "declined": Letter.objects.filter(status="declined").count(),
    }
    return render(
        request,
        "adminpanel/letters.html",
        {
            "letters": letters,
            "status": status,
            "search": search,
            "counts": counts,
        },
    )


@admin_required
def admin_letter_detail(request, pk):
    letter = get_object_or_404(Letter, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        note = request.POST.get("admin_note", "").strip()
        payment = getattr(settings, "LETTER_APPROVAL_PAYMENT", 25.00)

        if action == "approve" and letter.status == "pending":
            letter.status = "approved"
            letter.admin_note = note
            letter.earnings = payment
            letter.payout_credited = True
            letter.reviewed_at = timezone.now()
            letter.save()
            letter.user.balance += payment
            letter.user.total_earned += payment
            letter.user.save()
            _send_letter_email(letter, "approved", note)
            messages.success(
                request,
                f"Letter approved. ${payment} credited to {letter.user.username}. Email sent.",
            )

        elif action == "decline" and letter.status == "pending":
            letter.status = "declined"
            letter.admin_note = note
            letter.reviewed_at = timezone.now()
            letter.save()
            _send_letter_email(letter, "declined", note)
            messages.warning(
                request, f"Letter declined. Email sent to {letter.user.username}."
            )

        elif action == "reset":
            letter.status = "pending"
            letter.admin_note = ""
            letter.reviewed_at = None
            letter.earnings = 0
            letter.payout_credited = False
            letter.save()
            messages.info(request, "Letter reset to pending.")

        return redirect("adminpanel:letter_detail", pk=pk)

    return render(request, "adminpanel/letter_detail.html", {"letter": letter})


# ── Users ─────────────────────────────────────────────────
@admin_required
def admin_users(request):
    qs = User.objects.filter(is_staff=False).order_by("-date_joined")
    search = request.GET.get("q", "")
    if search:
        qs = qs.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )

    paginator = Paginator(qs, 15)
    users = paginator.get_page(request.GET.get("page", 1))
    return render(request, "adminpanel/users.html", {"users": users, "search": search})


@admin_required
def admin_user_detail(request, pk):
    u = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle_active":
            u.is_active = not u.is_active
            u.save()
            state = "activated" if u.is_active else "deactivated"
            messages.success(request, f"User {u.username} {state}.")
        elif action == "adjust_balance":
            try:
                amount = Decimal(request.POST.get("amount", 0))
                mode = request.POST.get("mode", "add")
                if mode == "add":
                    u.balance += amount
                else:
                    u.balance = max(0, u.balance - amount)
                u.save()
                messages.success(request, f"Balance updated to ${u.balance:.2f}.")
            except ValueError:
                messages.error(request, "Invalid amount.")
        elif action == "send_email":
            subject = request.POST.get("subject", "")
            body = request.POST.get("body", "")
            send_mail(
                subject,
                body,
                getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@smartwritingfinance.com"
                ),
                [u.email],
                fail_silently=True,
            )
            messages.success(request, f"Email sent to {u.email}.")
        return redirect("adminpanel:user_detail", pk=pk)

    letters = Letter.objects.filter(user=u).order_by("-submitted_at")
    deposits = Deposit.objects.filter(user=u).order_by("-created_at")[:5]
    withdrawals = Withdrawal.objects.filter(user=u).order_by("-created_at")[:5]
    return render(
        request,
        "adminpanel/user_detail.html",
        {
            "u": u,
            "letters": letters,
            "deposits": deposits,
            "withdrawals": withdrawals,
        },
    )


# ── Deposits ──────────────────────────────────────────────
@admin_required
def admin_deposits(request):
    qs = Deposit.objects.select_related("user").all()
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)

    if request.method == "POST":
        dep_id = request.POST.get("deposit_id")
        action = request.POST.get("action")
        dep = get_object_or_404(Deposit, pk=dep_id)
        if action == "confirm" and dep.status == "pending":
            dep.status = "confirmed"
            dep.confirmed_at = timezone.now()
            dep.save()
            dep.user.balance += dep.amount_usd
            dep.user.save()
            send_mail(
                f"💰 Deposit of ${dep.amount_usd} Confirmed",
                f"Hi {dep.user.first_name or dep.user.username},\n\n"
                f"Your {dep.method} deposit of ${dep.amount_usd} has been confirmed and credited to your balance.\n\n"
                f"— Smart Writing Finance Team",
                getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@smartwritingfinance.com"
                ),
                [dep.user.email],
                fail_silently=True,
            )
            messages.success(request, f"Deposit confirmed. ${dep.amount_usd} credited.")
        elif action == "fail" and dep.status == "pending":
            dep.status = "failed"
            dep.save()
            messages.warning(request, "Deposit marked as failed.")
        return redirect("adminpanel:deposits")

    paginator = Paginator(qs, 15)
    deposits = paginator.get_page(request.GET.get("page", 1))
    counts = {
        "all": Deposit.objects.count(),
        "pending": Deposit.objects.filter(status="pending").count(),
        "confirmed": Deposit.objects.filter(status="confirmed").count(),
        "failed": Deposit.objects.filter(status="failed").count(),
    }
    return render(
        request,
        "adminpanel/deposits.html",
        {
            "deposits": deposits,
            "status": status,
            "counts": counts,
        },
    )


# ── Withdrawals ───────────────────────────────────────────
@admin_required
def admin_withdrawals(request):
    qs = Withdrawal.objects.select_related("user").all()
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)

    if request.method == "POST":
        w_id = request.POST.get("withdrawal_id")
        action = request.POST.get("action")
        w = get_object_or_404(Withdrawal, pk=w_id)
        if action == "complete" and w.status in ("pending", "processing"):
            w.status = "completed"
            w.processed_at = timezone.now()
            w.save()
            send_mail(
                f"✅ Withdrawal of ${w.amount} Completed",
                f"Hi {w.user.first_name or w.user.username},\n\n"
                f"Your withdrawal of ${w.amount} to {w.bank_name} has been processed successfully.\n\n"
                f"— Smart Writing Finance Team",
                getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@smartwritingfinance.com"
                ),
                [w.user.email],
                fail_silently=True,
            )
            messages.success(request, f"Withdrawal completed. Email sent.")
        elif action == "reject" and w.status in ("pending", "processing"):
            w.status = "rejected"
            w.processed_at = timezone.now()
            w.save()
            w.user.balance += w.amount
            w.user.save()
            send_mail(
                f"❌ Withdrawal of ${w.amount} Rejected",
                f"Hi {w.user.first_name or w.user.username},\n\n"
                f"Your withdrawal request of ${w.amount} has been rejected. "
                f"The amount has been refunded to your balance.\n\n"
                f"— Smart Writing Finance Team",
                getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@smartwritingfinance.com"
                ),
                [w.user.email],
                fail_silently=True,
            )
            messages.warning(
                request, "Withdrawal rejected. Balance refunded. Email sent."
            )
        elif action == "processing" and w.status == "pending":
            w.status = "processing"
            w.save()
            messages.info(request, "Withdrawal marked as processing.")
        return redirect("adminpanel:withdrawals")

    paginator = Paginator(qs, 15)
    withdrawals = paginator.get_page(request.GET.get("page", 1))
    counts = {
        "all": Withdrawal.objects.count(),
        "pending": Withdrawal.objects.filter(status="pending").count(),
        "processing": Withdrawal.objects.filter(status="processing").count(),
        "completed": Withdrawal.objects.filter(status="completed").count(),
        "rejected": Withdrawal.objects.filter(status="rejected").count(),
    }
    return render(
        request,
        "adminpanel/withdrawals.html",
        {
            "withdrawals": withdrawals,
            "status": status,
            "counts": counts,
        },
    )
