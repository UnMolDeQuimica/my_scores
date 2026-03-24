import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q

from .models import Score, Group
from .forms import ScoreUploadForm, GroupForm, LoginForm


# ──────────────────────────────────────────
# Auth
# ──────────────────────────────────────────

def landing_page(request):
    """Landing page for unauthenticated users."""
    if request.user.is_authenticated:
        return redirect('score_viewer')
    return render(request, 'scores/landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('score_viewer')

    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        # Django auth uses username by default; we look up user by email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            error = 'Invalid email or password.'

    return render(request, 'scores/login.html', {'form': form, 'error': error})


def logout_view(request):
    logout(request)
    return redirect('landing')


# ──────────────────────────────────────────
# Score Viewer (OSMD)
# ──────────────────────────────────────────

@login_required
def score_viewer(request):
    """Main OSMD viewer page — default view after login."""
    scores = Score.objects.filter(owner=request.user)
    groups = Group.objects.all()
    return render(request, 'scores/viewer.html', {
        'scores': scores,
        'groups': groups,
    })


@login_required
@require_GET
def score_file(request, pk):
    """Serve score file content for OSMD to load."""
    score = get_object_or_404(Score, pk=pk, owner=request.user)
    with score.file.open('rb') as f:
        content = f.read()

    ext = score.file.name.rsplit('.', 1)[-1].lower()
    if ext == 'mxl':
        content_type = 'application/vnd.recordare.musicxml'
    else:
        content_type = 'application/xml'

    from django.http import HttpResponse
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{score.name}.{ext}"'
    return response


@login_required
@require_GET
def api_scores(request):
    """JSON API: list user scores with optional filters."""
    scores = Score.objects.filter(owner=request.user)

    name = request.GET.get('name', '').strip()
    author = request.GET.get('author', '').strip()
    group_id = request.GET.get('group', '').strip()

    if name:
        scores = scores.filter(name__icontains=name)
    if author:
        scores = scores.filter(author__icontains=author)
    if group_id:
        scores = scores.filter(groups__id=group_id)

    data = []
    for s in scores.distinct():
        data.append({
            'id': s.id,
            'name': s.name,
            'author': s.author,
            'groups': list(s.groups.values_list('name', flat=True)),
            'group_ids': list(s.groups.values_list('id', flat=True)),
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
            'file_url': f'/scores/{s.id}/file/',
        })

    return JsonResponse({'scores': data})


# ──────────────────────────────────────────
# Upload Score
# ──────────────────────────────────────────

@login_required
def upload_score(request):
    if request.method == 'POST':
        form = ScoreUploadForm(request.POST, request.FILES)
        if form.is_valid():
            score = form.save(commit=False)
            score.owner = request.user
            score.save()
            form.save_m2m()
            return redirect('score_viewer')
    else:
        form = ScoreUploadForm()
    groups = Group.objects.all()
    return render(request, 'scores/upload.html', {'form': form, 'groups': groups})


# ──────────────────────────────────────────
# Score List (editable table)
# ──────────────────────────────────────────

@login_required
def score_list(request):
    scores = Score.objects.filter(owner=request.user)
    groups = Group.objects.all()
    return render(request, 'scores/score_list.html', {
        'scores': scores,
        'groups': groups,
    })


@login_required
@require_POST
def score_update(request, pk):
    """AJAX endpoint to update a score field inline."""
    score = get_object_or_404(Score, pk=pk, owner=request.user)
    data = json.loads(request.body)

    field = data.get('field')
    value = data.get('value')

    if field == 'name':
        if not value or not value.strip():
            return JsonResponse({'error': 'Name is required.'}, status=400)
        # Check uniqueness
        if Score.objects.filter(name=value.strip()).exclude(pk=pk).exists():
            return JsonResponse({'error': 'A score with this name already exists.'}, status=400)
        score.name = value.strip()
        score.save()
    elif field == 'author':
        score.author = value.strip() if value else ''
        score.save()
    elif field == 'groups':
        # value is a list of group IDs
        group_ids = value if isinstance(value, list) else []
        score.groups.set(group_ids)
    else:
        return JsonResponse({'error': 'Invalid field.'}, status=400)

    return JsonResponse({'ok': True})


@login_required
@require_POST
def score_delete(request, pk):
    """Delete a score."""
    score = get_object_or_404(Score, pk=pk, owner=request.user)
    score.file.delete(save=False)
    score.delete()
    return JsonResponse({'ok': True})


# ──────────────────────────────────────────
# Groups CRUD
# ──────────────────────────────────────────

@login_required
def group_list(request):
    groups = Group.objects.all()
    form = GroupForm()
    return render(request, 'scores/groups.html', {'groups': groups, 'form': form})


@login_required
@require_POST
def group_create(request):
    form = GroupForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True, 'id': form.instance.id, 'name': form.instance.name})
    return JsonResponse({'error': form.errors}, status=400)


@login_required
@require_POST
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)
    if Group.objects.filter(name=name).exclude(pk=pk).exists():
        return JsonResponse({'error': 'A group with this name already exists.'}, status=400)
    group.name = name
    group.save()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    return JsonResponse({'ok': True})
