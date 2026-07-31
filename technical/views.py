from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Concept, TechQuestion, UserTechProgress


@login_required
def concept_list(request):
    concept_qs = Concept.objects.all().order_by('rank')

    domain = request.GET.get('domain', '')
    if domain:
        concept_qs = concept_qs.filter(domain=domain)

    paginator = Paginator(concept_qs, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'technical/concept_list.html', {
        'page_obj': page_obj,
        'domains': Concept.DOMAIN,
        'selected_domain': domain,
    })


@login_required
def concept_detail(request, rank):
    concept = get_object_or_404(Concept, rank=rank)
    prev_concept = Concept.objects.filter(rank__lt=rank).order_by('-rank').first()
    next_concept = Concept.objects.filter(rank__gt=rank).order_by('rank').first()
    return render(request, 'technical/concept_detail.html', {
        'concept': concept,
        'prev_concept': prev_concept,
        'next_concept': next_concept,
    })


@login_required
def question_list(request):
    questions = TechQuestion.objects.all()
    solved_ids = set(UserTechProgress.objects.filter(user=request.user, solved=True).values_list('question_id', flat=True))
    domains = {}
    for q in questions:
        domains.setdefault(q.get_domain_display(), []).append(q)
    total = questions.count()
    done = len(solved_ids)
    return render(request, 'technical/question_list.html', {
        'domains': domains, 'solved_ids': solved_ids, 'total': total, 'done': done,
        'pct': round(done / total * 100) if total else 0,
    })


@require_POST
@login_required
def toggle_question(request, qid):
    question = get_object_or_404(TechQuestion, id=qid)
    progress, _ = UserTechProgress.objects.get_or_create(user=request.user, question=question)
    progress.solved = not progress.solved
    progress.save()
    if progress.solved:
        from core.views import log_activity, check_pirate_king
        log_activity(request.user)
        check_pirate_king(request.user)
    return JsonResponse({'solved': progress.solved})
