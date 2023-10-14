from django.urls import include, path

from grafita.urls import urls
from rest.urls import router

urlpatterns = [
    path('api/v1/', include(router.urls), name='api'),
]

urlpatterns += urls
