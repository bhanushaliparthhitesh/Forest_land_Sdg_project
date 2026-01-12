from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_data, name='add'),
    path('analyze/', views.analyze, name='analyze'),
    path('predict/', views.predict, name='predict'),
    path('visualize/', views.visualize, name='visualize'),
]
