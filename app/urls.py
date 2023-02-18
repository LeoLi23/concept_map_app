from django.urls import path
from . import views

app_name = 'app'  # specify the app name

urlpatterns = [
    path('', views.index, name='index'),
    path('createConcept/', views.createConcept, name='createConcept'),
    path('updateConcept/', views.updateConcept, name='updateConcept'),
]
