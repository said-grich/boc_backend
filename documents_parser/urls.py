from django.urls import path
from .views import DeleteExtractedDataBySearchIDView, ExportSearchResultsView, History, ListExtractedDataView, SearchView ,search_page
from django.urls import path, include
urlpatterns = [
    path('api/search/', SearchView.as_view(), name='search'),
    path('api/export-search-results/<str:search_id>/', ExportSearchResultsView.as_view(), name='export-search-results'),
    path('search/', search_page, name='search_page'),
    path('history/', History , name='history_page'),
    path('api/history/', ListExtractedDataView.as_view() , name='user_record'),
    path('api/history/delete/<uuid:search_id>/', DeleteExtractedDataBySearchIDView.as_view() , name='user_record'),

    
]
