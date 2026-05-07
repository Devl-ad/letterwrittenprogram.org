import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from apps.letters.models import Letter


def home_page(request):
    return render(request, "index.html")


@login_required
def dashboard_index(request):
    user = request.user
    letters = Letter.objects.filter(user=user)
    today = datetime.date.today()

    this_month = (
        letters.filter(
            status="approved",
            reviewed_at__month=today.month,
            reviewed_at__year=today.year,
        ).aggregate(total=Sum("earnings"))["total"]
        or 0
    )

    stats = {
        "total": letters.count(),
        "pending": letters.filter(status="pending").count(),
        "approved": letters.filter(status="approved").count(),
        "declined": letters.filter(status="declined").count(),
        "total_earned": user.total_earned,
        "balance": user.balance,
        "pending_payout": user.pending_payout,
        "this_month": this_month,
    }

    recent_letters = letters[:5]
    recent_earnings = letters.filter(status="approved").order_by("-reviewed_at")[:4]

    return render(
        request,
        "dashboard/index.html",
        {
            "stats": stats,
            "recent_letters": recent_letters,
            "recent_earnings": recent_earnings,
        },
    )
