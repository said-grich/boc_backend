from django.urls import path
from .views import SearchView

urlpatterns = [
    path('github-search/', SearchView.as_view(), name='github-search'),
]