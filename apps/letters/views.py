from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Letter
from .forms import LetterForm


@login_required
def write_letter(request):
    if request.method == "POST":
        form = LetterForm(request.POST)
        if form.is_valid():
            letter = form.save(commit=False)
            letter.user = request.user
            letter.save()
            messages.success(request, f'Letter "{letter.title}" submitted for review!')
            return redirect("letters:detail", pk=letter.pk)
    else:
        form = LetterForm()
    return render(request, "dashboard/write_letter.html", {"form": form})


@login_required
def letter_list(request):
    letters = Letter.objects.filter(user=request.user)
    status = request.GET.get("status", "")
    search = request.GET.get("search", "")
    if status:
        letters = letters.filter(status=status)
    if search:
        letters = letters.filter(title__icontains=search)
    return render(
        request,
        "dashboard/view_letters.html",
        {
            "letters": letters,
            "form": "form",
            "total": letters.count(),
            "pending_count": Letter.objects.filter(
                user=request.user, status="pending"
            ).count(),
            "approved_count": Letter.objects.filter(
                user=request.user, status="approved"
            ).count(),
            "declined_count": Letter.objects.filter(
                user=request.user, status="declined"
            ).count(),
        },
    )


@login_required
def letter_detail(request, pk):
    letter = get_object_or_404(Letter, pk=pk, user=request.user)
    return render(request, "dashboard/letter_detail.html", {"letter": letter})
