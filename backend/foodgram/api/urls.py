from rest_framework.authtoken import views
from django.urls import path, include, re_path

from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
     path('', include(router.urls)),
     #path('', include('djoser.urls')),
     path('auth/', include('djoser.urls.authtoken')),
]