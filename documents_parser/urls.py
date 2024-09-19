from django.urls import path
from .views import ExportSearchResultsView, SearchView

urlpatterns = [
    path('api/search/', SearchView.as_view(), name='search'),
    path('api/export-search-results/<str:search_id>/', ExportSearchResultsView.as_view(), name='export-search-results'),
]