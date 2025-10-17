from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação com templates personalizados
    path('entrar/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),

    # Registro e perfil
    path('cadastrar/', views.register, name='register'),
    path('minha-conta/', views.profile, name='profile'),
]
