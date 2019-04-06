from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='News-Home'),
    path('about/', views.home, name='News-About'),
    path('vote/', views.vote, name='News-vote'),
    path('faq/', views.faq, name='news-faq'),
]


def get_client_ip(request):
    meta = request.META.get('HTTP_X_FORWARDED_FOR')
    if meta:
        ip_address = meta.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address
