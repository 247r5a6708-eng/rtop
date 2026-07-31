from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from .models import ActivityLog, Profile, Badge, Quote, ONE_PIECE_MILESTONES
from .forms import ProfileForm
from dsa.models import Question, UserQuestionProgress
from aptitude.models import Problem, UserProblemProgress
from technical.models import TechQuestion, UserTechProgress
from interview.models import InterviewQuestion, UserInterviewProgress

COINS_PER_TASK = 5
COINS_PER_STREAK_REPAIR_DAY = 10


def home(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/landing.html')


def check_badges(user):
    """Award a new One Piece themed badge every 50 distinct active days."""
    total_days = ActivityLog.objects.filter(user=user, count__gt=0).count()
    new_badges = []
    for milestone, title, desc in ONE_PIECE_MILESTONES:
        if total_days >= milestone:
            badge, created = Badge.objects.get_or_create(
                user=user, milestone=milestone,
                defaults={'title': title, 'description': desc}
            )
            if created:
                new_badges.append(badge)
    return new_badges


def log_activity(user):
    """Log today's activity, award coins, and check for new badges."""
    today = timezone.localdate()
    log, _ = ActivityLog.objects.get_or_create(user=user, date=today)
    log.count += 1
    log.save()

    profile, _ = Profile.objects.get_or_create(user=user)
    profile.coins += COINS_PER_TASK
    profile.save(update_fields=['coins'])

    check_badges(user)


def check_pirate_king(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    dsa_total = Question.objects.count()
    dsa_done = UserQuestionProgress.objects.filter(user=user, solved=True).count()
    apti_total = Problem.objects.count()
    apti_done = UserProblemProgress.objects.filter(user=user, solved=True).count()
    tech_total = TechQuestion.objects.count()
    tech_done = UserTechProgress.objects.filter(user=user, solved=True).count()

    all_done = dsa_total and apti_total and tech_total and \
        dsa_done >= dsa_total and apti_done >= apti_total and tech_done >= tech_total

    if all_done and not profile.is_pirate_king:
        profile.is_pirate_king = True
        profile.crowned_at = timezone.now()
        profile.save()
    return profile


def current_streak(user):
    """Consecutive-day streak (git/LeetCode style), counting back from today (or yesterday)."""
    active_dates = set(ActivityLog.objects.filter(user=user, count__gt=0).values_list('date', flat=True))
    if not active_dates:
        return 0
    today = timezone.localdate()
    cursor = today if today in active_dates else today - timedelta(days=1)
    if cursor not in active_dates:
        return 0
    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def get_next_in_sequence(ordered_queryset, solved_ids):
    """
    Returns the first item (in the model's canonical curriculum order —
    e.g. DSA pattern order then question order, or Aptitude topic order,
    or Technical domain order) that the user hasn't solved yet.

    This is what makes progress sequential and user-paced: a user always
    sees the same "next" item until they check it off, at which point the
    challenge advances to the following item in the curriculum — it never
    jumps ahead on its own and never picks randomly. Once the whole list is
    solved, it wraps back to the very first item (for review) rather than
    showing nothing.
    """
    next_item = ordered_queryset.exclude(id__in=solved_ids).first()
    if next_item is not None:
        return next_item
    return ordered_queryset.first()


def get_daily_quote(series, seed_date):
    """
    Picks one Quote per day for the given series, strictly in order (by `order`,
    then id) starting from the first quote and moving forward one per day,
    wrapping back to the start once the list is exhausted. Never random.
    """
    quotes = list(Quote.objects.filter(series=series).order_by('order', 'id'))
    if not quotes:
        return None
    idx = seed_date.toordinal() % len(quotes)
    return quotes[idx]


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    dsa_total = Question.objects.count()
    dsa_done = UserQuestionProgress.objects.filter(user=request.user, solved=True).count()
    apti_total = Problem.objects.count()
    apti_done = UserProblemProgress.objects.filter(user=request.user, solved=True).count()
    tech_total = TechQuestion.objects.count()
    tech_done = UserTechProgress.objects.filter(user=request.user, solved=True).count()
    interview_total = InterviewQuestion.objects.count()
    interview_done = UserInterviewProgress.objects.filter(user=request.user, marked=True).count()

    def pct(done, total):
        return round((done / total) * 100, 1) if total else 0

    # Build 1-year calendar heatmap data (git-style)
    end = timezone.localdate()
    start = end - timedelta(days=364)
    logs = {l.date: l.count for l in ActivityLog.objects.filter(user=request.user, date__gte=start, date__lte=end)}
    calendar_data = []
    d = start
    while d <= end:
        calendar_data.append({'date': d.isoformat(), 'count': logs.get(d, 0)})
        d += timedelta(days=1)

    total_done = dsa_done + apti_done + tech_done
    total_all = dsa_total + apti_total + tech_total

    # ---- Daily Challenge: the next uncompleted DSA / Aptitude / Technical
    # item in curriculum order — e.g. DSA always starts at the Array pattern's
    # first question and only advances to the next pattern once the user has
    # solved everything before it. Never random, never date-jumped. ----
    today = timezone.localdate()
    dsa_solved_ids = UserQuestionProgress.objects.filter(user=request.user, solved=True).values_list('question_id', flat=True)
    apti_solved_ids = UserProblemProgress.objects.filter(user=request.user, solved=True).values_list('problem_id', flat=True)
    tech_solved_ids = UserTechProgress.objects.filter(user=request.user, solved=True).values_list('question_id', flat=True)

    daily_dsa = get_next_in_sequence(Question.objects.all(), dsa_solved_ids)
    daily_apti = get_next_in_sequence(Problem.objects.all(), apti_solved_ids)
    daily_tech = get_next_in_sequence(TechQuestion.objects.all(), tech_solved_ids)

    daily_dsa_solved = daily_dsa and UserQuestionProgress.objects.filter(
        user=request.user, question=daily_dsa, solved=True).exists()
    daily_apti_solved = daily_apti and UserProblemProgress.objects.filter(
        user=request.user, problem=daily_apti, solved=True).exists()
    daily_tech_solved = daily_tech and UserTechProgress.objects.filter(
        user=request.user, question=daily_tech, solved=True).exists()

    streak = current_streak(request.user)
    total_active_days = ActivityLog.objects.filter(user=request.user, count__gt=0).count()
    recent_badges = Badge.objects.filter(user=request.user).order_by('-awarded_at')[:3]
    next_milestone = next((m for m, t, d in ONE_PIECE_MILESTONES if m > total_active_days), None)

    daily_quote = get_daily_quote(Quote.ONE_PIECE, today)

    context = {
        'daily_quote': daily_quote,
        'profile': profile,
        'dsa_total': dsa_total, 'dsa_done': dsa_done, 'dsa_pct': pct(dsa_done, dsa_total),
        'apti_total': apti_total, 'apti_done': apti_done, 'apti_pct': pct(apti_done, apti_total),
        'tech_total': tech_total, 'tech_done': tech_done, 'tech_pct': pct(tech_done, tech_total),
        'interview_total': interview_total, 'interview_done': interview_done, 'interview_pct': pct(interview_done, interview_total),
        'overall_pct': pct(total_done, total_all),
        'calendar_data': calendar_data,
        'daily_dsa': daily_dsa, 'daily_dsa_solved': daily_dsa_solved,
        'daily_apti': daily_apti, 'daily_apti_solved': daily_apti_solved,
        'daily_tech': daily_tech, 'daily_tech_solved': daily_tech_solved,
        'streak': streak,
        'total_active_days': total_active_days,
        'recent_badges': recent_badges,
        'next_milestone': next_milestone,
    }
    return render(request, 'core/dashboard.html', context)


@require_POST
def toggle_theme(request):
    """Works for both logged-in and anonymous users (e.g. on the login page)."""
    current = request.session.get('theme', 'dark')
    new = 'light' if current == 'dark' else 'dark'
    request.session['theme'] = new
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.theme = new
        profile.save(update_fields=['theme'])
    return JsonResponse({'theme': new})


@login_required
def profile_view(request):
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    from accounts.forms import EmailChangeForm

    profile, _ = Profile.objects.get_or_create(user=request.user)

    form = ProfileForm(instance=profile)
    email_form = EmailChangeForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'profile')

        if action == 'profile':
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Your bounty poster has been updated, nakama!")
                return redirect('core:profile')

        elif action == 'change_email':
            email_form = EmailChangeForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, "Your email has been updated, nakama!")
                return redirect('core:profile')

        elif action == 'change_password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # keep the user logged in
                messages.success(request, "Your password has been changed, nakama! Stay safe out there.")
                return redirect('core:profile')

    streak = current_streak(request.user)
    total_active_days = ActivityLog.objects.filter(user=request.user, count__gt=0).count()
    earned = {b.milestone: b for b in Badge.objects.filter(user=request.user)}
    badge_board = []
    for milestone, title, desc in ONE_PIECE_MILESTONES:
        badge_board.append({
            'milestone': milestone, 'title': title, 'description': desc,
            'earned': milestone in earned,
            'awarded_at': earned[milestone].awarded_at if milestone in earned else None,
        })

    # Missed days in the last 60, eligible for a coin-powered streak repair
    end = timezone.localdate()
    start = end - timedelta(days=59)
    active_dates = set(ActivityLog.objects.filter(
        user=request.user, date__gte=start, date__lt=end, count__gt=0).values_list('date', flat=True))
    missed_days = []
    d = start
    while d < end:
        if d not in active_dates:
            missed_days.append(d)
        d += timedelta(days=1)
    missed_days = list(reversed(missed_days))[:30]

    nakama_quote = get_daily_quote(Quote.ATTACK_ON_TITAN, timezone.localdate())

    context = {
        'profile': profile,
        'form': form,
        'email_form': email_form,
        'password_form': password_form,
        'streak': streak,
        'total_active_days': total_active_days,
        'badge_board': badge_board,
        'missed_days': missed_days,
        'repair_cost': COINS_PER_STREAK_REPAIR_DAY,
        'nakama_quote': nakama_quote,
    }
    return render(request, 'core/profile.html', context)


@require_POST
@login_required
def restore_streak(request):
    """Spend coins to backfill a missed day on the Voyage Log (like a LeetCode streak freeze)."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    date_str = request.POST.get('date', '')
    try:
        target = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "That's not a valid date, nakama.")
        return redirect('core:profile')

    today = timezone.localdate()
    if target >= today:
        messages.error(request, "You can only repair past days, not today or the future.")
        return redirect('core:profile')
    if (today - target).days > 60:
        messages.error(request, "That day is too far in the past to repair.")
        return redirect('core:profile')

    existing = ActivityLog.objects.filter(user=request.user, date=target, count__gt=0).exists()
    if existing:
        messages.info(request, "That day already has logged activity — no repair needed.")
        return redirect('core:profile')

    if profile.coins < COINS_PER_STREAK_REPAIR_DAY:
        messages.error(request, f"Not enough coins! You need {COINS_PER_STREAK_REPAIR_DAY} coins to repair a day.")
        return redirect('core:profile')

    log, _ = ActivityLog.objects.get_or_create(user=request.user, date=target)
    log.count = max(log.count, 1)
    log.save()
    profile.coins -= COINS_PER_STREAK_REPAIR_DAY
    profile.save(update_fields=['coins'])
    check_badges(request.user)
    messages.success(request, f"Voyage Log repaired for {target.strftime('%d %b %Y')}! Streak restored.")
    return redirect('core:profile')