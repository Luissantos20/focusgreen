from django.urls import path
from . import views

urlpatterns = [
    path('', views.tracker_view, name='tracker'),
    path('add_entry/', views.add_entry, name='add_entry'),  # <- Nova rota AJAX
]
