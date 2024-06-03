from django.urls import path
from .views import dashboard_view
from .views import main

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('main', main, name='main'),
]
