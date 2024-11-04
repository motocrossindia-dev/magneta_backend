from django.urls import path

from advertisements.view.Banner import banners


app_name = 'advertisements'

urlpatterns = [
    path('banners/', banners, name='banners'),
]
