def theme_and_progress(request):
    theme = request.session.get('theme', 'dark')
    ctx = {'active_theme': theme, 'nav_profile': None}
    if request.user.is_authenticated:
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=request.user)
        ctx['nav_profile'] = profile
    return ctx
