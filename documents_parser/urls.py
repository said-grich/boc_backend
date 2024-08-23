<<<<<<< HEAD
from django.urls import path
from .views import SearchView

urlpatterns = [
    path('github-search/', SearchView.as_view(), name='github-search'),
=======
from django.urls import path
from .views import SearchView

urlpatterns = [
    path('github-search/', SearchView.as_view(), name='github-search'),
>>>>>>> 9f1546fdcea49d1c9a56afe48dd77b158a96336d
]