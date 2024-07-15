from django.urls import path
from .views import GitHubSearchView

urlpatterns = [
    path('github-search/', GitHubSearchView.as_view(), name='github-search'),
]