from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Class-Based Views(Transforma as classes Login view e Logout em uma function)
    path('entrar/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    # Function-based views
    path('cadastrar/', views.register, name='register'),
    path('minha-conta/', views.profile, name='profile'),
]
