from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', views.IngredientViewSet)
router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = (
    path('', include(router.urls)),
    path('users/subscriptions/', views.SubscriptionViewSet.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:pk>/subscribe/', views.SubscribeView.as_view()),
)
