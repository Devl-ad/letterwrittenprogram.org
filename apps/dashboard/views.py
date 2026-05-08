import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from apps.letters.models import Letter
from apps.accounts.models import Kyc
from apps.accounts.forms import KycForm


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


@login_required
def kyc(request):
    user = request.user
    doc = Kyc.objects.filter(user=user).first()

    if request.method == "POST":

        # prevent resubmitting approved/processing docs
        if doc and doc.status in ["processing", "approved"]:
            messages.warning(request, "Your KYC is already submitted.")
            return redirect("dashboard:kyc")

        form = KycForm(request.POST, request.FILES, instance=doc)

        if form.is_valid():

            # SAVE USER INFO
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.phone = request.POST.get("phone")
            user.country = request.POST.get("country")
            user.save()

            # SAVE KYC
            kyc_doc = form.save(commit=False)
            kyc_doc.user = user
            kyc_doc.status = "processing"
            kyc_doc.is_approved = False
            kyc_doc.save()

            messages.success(request, "Document submitted successfully.")
            return redirect("dashboard:kyc")

        else:
            print(form.errors)
            messages.error(request, "Something went wrong.")

    else:
        form = KycForm(instance=doc)

    return render(
        request,
        "dashboard/kyc.html",
        {
            "doc": doc,
            "form": form,
        },
    )
