from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages  
import json
from .models import ScreenTimeEntry
from .forms import ScreenTimeEntryForm


@login_required
def tracker_view(request):
    form = ScreenTimeEntryForm()

    if request.method == 'POST':
        form = ScreenTimeEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.started_at = timezone.now()
            entry.save()
            messages.success(request, "Tempo adicionado com sucesso! 🌿")
            return redirect('tracker')
        else:
            messages.error(request, "Erro ao adicionar tempo. Verifique os campos.")

    entries = ScreenTimeEntry.objects.filter(user=request.user).order_by('-started_at')

    return render(request, 'tracker/tracker.html', {'form': form, 'entries': entries})


# --------------------------------------------------------
# VIEW AJAX - Timer JS
# --------------------------------------------------------
@login_required
def add_entry(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        minutes = int(data.get('minutes', 0))
        category = data.get('category')
        note = data.get('note', '')

        if minutes <= 0:
            return JsonResponse({'success': False, 'error': 'Minutos inválidos'}, status=400)
        if category not in dict(ScreenTimeEntry.CATEGORY_CHOICES):
            return JsonResponse({'success': False, 'error': 'Categoria inválida'}, status=400)

        entry = ScreenTimeEntry.objects.create(
            user=request.user,
            minutes=minutes,
            category=category,
            note=note
        )

        return JsonResponse({
            'success': True,
            'message': 'Tempo adicionado com sucesso! 🌱',
            'entry': {
                'id': entry.id,
                'minutes': entry.minutes,
                'category': entry.get_category_display(),
                'note': entry.note or '',
                'started_at': entry.started_at.strftime('%d/%m %H:%M'),
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
