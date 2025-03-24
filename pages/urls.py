from django.urls import path
from .views import render_page 

urlpatterns = [
    path('', render_page, name='render_page'),
    path('<path:title>/', render_page, name='render_page'),
]