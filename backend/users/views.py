from django.shortcuts import get_object_or_404
from recipes.pagination import CustomPagination
from rest_framework import status, views
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Follow, User
from users.serializers import SubscribeSerializer, SubscriptionSerializer


class SubscriptionViewSet(ListAPIView):
    """
    Представление для получения списка подписок пользователя.

    Атрибуты:
        serializer_class (type): Класс сериализатора для подписок.
        pagination_class (type): Класс пагинации.
        permission_classes (tuple): Классы разрешений.

    """

    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Получает список подписок текущего пользователя.

        Returns:
            QuerySet: QuerySet подписок текущего пользователя.

        """
        user = self.request.user
        return user.follower.all()


class SubscribeView(views.APIView):
    """
    Представление для подписки и отписки от других пользователей.

    Атрибуты:
        pagination_class (type): Класс пагинации.
        permission_classes (tuple): Классы разрешений.

    """

    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        """
        Создает подписку на указанного пользователя.

        Args:
            request (Request): HTTP-запрос.
            pk (int): Идентификатор пользователя, на которого осуществляется подписка.

        Returns:
            Response: HTTP-ответ с данными о созданной подписке.

        """
        author = get_object_or_404(User, pk=pk)
        user = self.request.user
        data = {'author': author.id, 'user': user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """
        Удаляет подписку на указанного пользователя.

        Args:
            request (Request): HTTP-запрос.
            pk (int): Идентификатор пользователя, от которого осуществляется отписка.

        Returns:
            Response: HTTP-ответ с кодом 204 (Без содержания).

        """
        author = get_object_or_404(User, pk=pk)
        user = self.request.user
        subscription = get_object_or_404(
            Follow, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)