from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import ScreenTimeEntryForm
from .models import ScreenTimeEntry

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
            return redirect('tracker')  # Redireciona para a própria página (atualiza a lista)

    entries = ScreenTimeEntry.objects.filter(user=request.user).order_by('-started_at')

    context = {
        'form': form,
        'entries': entries
    }
    return render(request, 'tracker/tracker.html', context)

