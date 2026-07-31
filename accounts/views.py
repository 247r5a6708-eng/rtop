from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from .forms import PirateRegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        form = PirateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            from core.models import Profile
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Welcome aboard, nakama! Your journey to the One Piece begins now.")
            return redirect('core:dashboard')
    else:
        form = PirateRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=identifier, password=password)
        if user is None:
            try:
                u = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, "Invalid credentials, sea dog. Try again.")
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have docked at port. See you soon, nakama!")
    return redirect('accounts:login')


class PirateResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.txt'
    html_email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class PirateResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class PirateResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class PirateResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
