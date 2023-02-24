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
    path('removeConnection/', views.removeConnection, name='removeConnection'),
    # recording
    path('startRecording/', views.startRecording, name='startRecording'),
    path('stopRecording/', views.stopRecording, name='stopRecording'),
    # Sync
    path('get_latest_nodes/<str:latestCheckTime>/', views.get_latest_nodes, name='get_latest_nodes'),
]
