from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm # Classe pronta do Django que cria o formulário de cadastro de usuário.
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) 
        if form.is_valid():
            # Registra um usuário no banco de dados automaticamente, sem precisar criar um models para ele.
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

