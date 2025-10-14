from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='assistant_index'),
]
