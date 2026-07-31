from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import InterviewQuestion, UserInterviewProgress


@login_required
def question_list(request):
    questions = InterviewQuestion.objects.all()
    marked_ids = set(UserInterviewProgress.objects.filter(user=request.user, marked=True).values_list('question_id', flat=True))
    total = questions.count()
    done = len(marked_ids)
    return render(request, 'interview/question_list.html', {
        'questions': questions, 'marked_ids': marked_ids, 'total': total, 'done': done,
        'pct': round(done / total * 100) if total else 0,
    })


@require_POST
@login_required
def toggle_question(request, qid):
    question = get_object_or_404(InterviewQuestion, id=qid)
    progress, _ = UserInterviewProgress.objects.get_or_create(user=request.user, question=question)
    progress.marked = not progress.marked
    progress.save()
    return JsonResponse({'marked': progress.marked})
