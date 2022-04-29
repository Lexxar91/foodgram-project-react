from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Exists, OuterRef, Sum
from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.pdf.create_pdf import create_pdf
from recipes.models import AmountIngredient

from recipes.models import Recipe

from .permissions import IsOwnerOrReadOnly
from recipes.models import Ingredient, Tag

from users.models import Follow
from .serializers import CustomUserSerializer, FavoriteAndShoppingSerializer, FollowSerializer, GetTokenSerializer, IngredientSerializer, RecipeSerializer, ResetPasswordSerializer, TagSerializer
from .mixins import CreateOrDeleteMixins, ListCreateRetrieveMixins
from users.models import User


class UserViewSet(ListCreateRetrieveMixins):
    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'list' or 'create':
            return (AllowAny(),)
        return IsAuthenticated()

    def get_serializer_class(self):
        if self.action == 'set_password':
            return ResetPasswordSerializer
        if self.action == 'subscriptions':
            return  FollowSerializer
        return CustomUserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            subscriptions = user.subscribing.filter(id=OuterRef('id'))
            return User.objects.annotate(is_subscribed=Exists(subscriptions))
        return User.objects.all()

    @action(methods=('GET'), detail=False, url_path='me')
    def me(self, request):
        user = request.user 
        serializer = self.get_serializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=('GET'), detail=False, url_path='subscriptions')
    def subscriptions(self, request):
         user = request.user 
         queryset = user.subscribing.annotate(
             is_subscribed = Exists(Follow.objects.filter(user=user, author=OuterRef('id')))
         ).perfetch_related('recipes').all()
         
         page = self.paginate_queryset(queryset)

         if page:
            serializer = self.get_serializer(page, many=True)

         serializer = self.get_serializer(queryset, many=True)

         return self.get_paginated_response(serializer.data)

    @action(methods=('POST'),url_path='set_password',detail=False)
    def set_password(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)
    filter_backend = (SearchFilter,)
    search_filter = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return (AllowAny(),)
        elif self.action == 'update' or self.action == 'destroy' or self.action == 'partial_update':
            return (IsOwnerOrReadOnly(),)
        else:
            return (IsAuthenticated(),)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            favorite = user.favorite_recipes.filter(id=OuterRef('id'))
            shopping_cart = user.shopping_cart.filter(id=OuterRef('id'))
            return Recipe.objects.annotate(
                is_favorited = Exists(favorite),
                is_in_shopping_cart = Exists(shopping_cart)
            )
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def download_shopping_cart(self, request):
        user = request.user
        ingredient_list = (
            AmountIngredient.objects.
            prefetch_related('ingredient', 'recipe').
            filter(recipe__shoppings=user).
            values('ingredient__id').
            order_by('ingredient__id')
        )

        shopping_list = (
            ingredient_list.annotate(amount=Sum('quantity')).
            values_list(
                'ingredient__name', 'ingredient__measurement_unit', 'amount'
            )
        )

        file = create_pdf(shopping_list, 'Список покупок')

        return FileResponse(
            file,
            as_attachment=True,
            filename='shopping_list.pdf',
            status=status.HTTP_200_OK
        )


class FavoriteViewSet(CreateOrDeleteMixins):
    permission_classes = (IsAuthenticated,)
    model_class = Recipe

    def get_queryset(self):
        user = self.request.user
        return user.favorite_recipes

    def get_serializer(self, id):
        return FavoriteAndShoppingSerializer(
            data={
                'recipe': id,
                'user': self.request.user.id,
                'type_list': 'favorite',
            },
            context={
                'request': self.request,
            }
        ) 

class ShoppingListViewSet(CreateOrDeleteMixins):
    permission_classes = (IsAuthenticated,)
    model_class = Recipe
  

    def get_queryset(self):
        user = self.request.user
        return user.shopping_recipes

    def get_serializer(self, id):
        return FavoriteAndShoppingSerializer(
            data={
                'recipe': id,
                'user': self.request.user.id,
                'type_list': 'shopping',
            },
            context={
                'request': self.request,
            }
        )
        
class TagViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    

class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (SearchFilter, )
    search_fields = ('name', )


class FollowViewSet(CreateOrDeleteMixins):
    permission_classes = (IsAuthenticated,)
    model_class = User
    

    def get_queryset(self):
        user = self.request.user
        return user.subscribing

    def get_serializer(self, id):
        return FollowSerializer(
            data={
                'author': id,
                'user': self.request.user.id,
                'type_list': 'shopping',
            },
            context={
                'request': self.request,
            }
        )
        


class GetTokenView(ObtainAuthToken):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, 
                email=serializer.validated_data['email']
            )
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'auth_token': token.key
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

   
class DelTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token = request.auth
        token.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )