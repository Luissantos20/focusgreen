from django.urls import path
from . import views

urlpatterns = [
    # Página principal do dashboard
    path('', views.index, name='dashboard'),

    # Endpoint auxiliar: dados dos últimos 7 dias (para gráfico via JS)
    path('data/7d/', views.data_last_7_days, name='dashboard_data_7d'),

    # Endpoint novo: dados completos para IA (JSON estruturado)
    path('insights-data/', views.insights_data, name='dashboard_insights_data'),
]
