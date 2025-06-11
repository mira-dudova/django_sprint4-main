from django.urls import path
from . import views

urlpatterns = [
    path('auth/registration/', views.registration, name='registration'),
]
