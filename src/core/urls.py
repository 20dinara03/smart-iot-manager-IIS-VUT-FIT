from django.urls import include, path

from grafita.urls import urls
from rest.urls import rest_urls

urlpatterns = [
    path('api/v1/', include(rest_urls), name='api'),
]

urlpatterns += urls
