from django.urls import path
from .views import get_process_store

app_name = 'process_store'

urlpatterns = [
    path('get_process_store/', get_process_store, name='get_process_store'),
]

