from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Topic, Problem, UserProblemProgress


@login_required
def topic_list(request):
    topics = Topic.objects.all()
    data = []
    for t in topics:
        total = t.problems.count()
        done = UserProblemProgress.objects.filter(user=request.user, problem__topic=t, solved=True).count()
        data.append({'topic': t, 'total': total, 'done': done, 'pct': round(done / total * 100) if total else 0})
    return render(request, 'aptitude/topic_list.html', {'topics': data})


@login_required
def topic_detail(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    problems = topic.problems.all()
    solved_ids = set(UserProblemProgress.objects.filter(user=request.user, problem__topic=topic, solved=True).values_list('problem_id', flat=True))
    return render(request, 'aptitude/topic_detail.html', {'topic': topic, 'problems': problems, 'solved_ids': solved_ids})


@require_POST
@login_required
def toggle_problem(request, pid):
    problem = get_object_or_404(Problem, id=pid)
    progress, _ = UserProblemProgress.objects.get_or_create(user=request.user, problem=problem)
    progress.solved = not progress.solved
    progress.save()
    if progress.solved:
        from core.views import log_activity, check_pirate_king
        log_activity(request.user)
        check_pirate_king(request.user)
    return JsonResponse({'solved': progress.solved})
