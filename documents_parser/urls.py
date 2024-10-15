from django.urls import path
from .views import ExportSearchResultsView, SearchView ,search_page
from django.urls import path, include
urlpatterns = [
    path('api/search/', SearchView.as_view(), name='search'),
    path('api/export-search-results/<str:search_id>/', ExportSearchResultsView.as_view(), name='export-search-results'),
    path('search/', search_page, name='search_page'),
    path('history/', History , name='History_page'),
]
