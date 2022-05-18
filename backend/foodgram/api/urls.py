from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import SubscribeView, SubscriptionViewSet

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', views.IngredientViewSet)
router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet, basename='recipe')


urlpatterns = (
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
)
