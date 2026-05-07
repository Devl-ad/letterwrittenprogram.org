from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileForm, PasswordChangeForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name or user.username}! Account created.")
        return redirect('dashboard:index')
    return render(request, 'dashboard/register.html', {'form': form})


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('accounts:profile')
    return render(request, 'dashboard/profile.html', {'form': form})


@login_required
def settings_view(request):
    pw_form = PasswordChangeForm(request.POST or None)
    has_2fa = False
    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice
        has_2fa = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
    except Exception:
        pass

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'change_password' and pw_form.is_valid():
            user = request.user
            if user.check_password(pw_form.cleaned_data['current_password']):
                user.set_password(pw_form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
            else:
                messages.error(request, "Current password is incorrect.")
            return redirect('accounts:settings')

        if action == 'disable_2fa':
            try:
                from django_otp.plugins.otp_totp.models import TOTPDevice
                TOTPDevice.objects.filter(user=request.user).delete()
            except Exception:
                pass
            request.user.two_fa_enabled = False
            request.user.save()
            messages.success(request, "Two-factor authentication disabled.")
            return redirect('accounts:settings')

    return render(request, 'dashboard/settings.html', {
        'pw_form': pw_form,
        'has_2fa': has_2fa,
    })
