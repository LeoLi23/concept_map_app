from django.urls import path
from . import views

app_name = 'app'  # specify the app name

urlpatterns = [
    path('', views.index, name='index'),
    # Concept
    path('createConcept/', views.createConcept, name='createConcept'),
    path('updateConcept/', views.updateConcept, name='updateConcept'),
    path('removeConcept/', views.removeConcept, name='removeConcept'),
    # Connection
    path('createConnection/', views.createConnection, name='createConnection'),

]
