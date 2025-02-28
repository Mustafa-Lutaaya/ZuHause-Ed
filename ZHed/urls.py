from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('zhed/', views.zhed, name='zhed'),
    path('whack/', views.whack, name='whack'),
]