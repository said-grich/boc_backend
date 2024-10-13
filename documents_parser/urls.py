from django.urls import path
from .views import ExportSearchResultsView, SearchView ,search_page

urlpatterns = [
    path('api/search/', SearchView.as_view(), name='search'),
    path('api/export-search-results/<str:search_id>/', ExportSearchResultsView.as_view(), name='export-search-results'),
    path('search/', search_page, name='search_page'),
    path('api/accounts/', include('accounts.urls')),
]
