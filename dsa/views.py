from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Pattern, Question, UserQuestionProgress


@login_required
def pattern_list(request):
    patterns = Pattern.objects.all()
    data = []
    for p in patterns:
        total = p.questions.count()
        done = UserQuestionProgress.objects.filter(user=request.user, question__pattern=p, solved=True).count()
        data.append({'pattern': p, 'total': total, 'done': done,
                     'pct': round(done / total * 100) if total else 0})
    return render(request, 'dsa/pattern_list.html', {'patterns': data})


@login_required
def pattern_detail(request, slug):
    pattern = get_object_or_404(Pattern, slug=slug)
    questions = pattern.questions.all()
    solved_ids = set(UserQuestionProgress.objects.filter(user=request.user, question__pattern=pattern, solved=True).values_list('question_id', flat=True))
    return render(request, 'dsa/pattern_detail.html', {'pattern': pattern, 'questions': questions, 'solved_ids': solved_ids})


@require_POST
@login_required
def toggle_question(request, qid):
    question = get_object_or_404(Question, id=qid)
    progress, _ = UserQuestionProgress.objects.get_or_create(user=request.user, question=question)
    progress.solved = not progress.solved
    progress.save()
    if progress.solved:
        from core.views import log_activity, check_pirate_king
        log_activity(request.user)
        check_pirate_king(request.user)
    return JsonResponse({'solved': progress.solved})
