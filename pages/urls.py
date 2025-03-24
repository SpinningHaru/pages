from django.urls import path
from .views import render_page

urlpatterns = [
    path('<path:title>/', render_page, name='render_page'),
]