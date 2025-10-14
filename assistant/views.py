from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import get_ai_insight

@login_required
def index(request):
    """Gera e exibe o insight personalizado da IA baseado nos dados do dashboard."""
    ai_response = None

    if request.method == 'POST':
        ai_response = get_ai_insight(request.user)

    return render(request, 'assistant/index.html', {
        'ai_response': ai_response
    })

