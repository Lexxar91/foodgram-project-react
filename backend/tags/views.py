from recipes.mixins import RetrieveListMixins
from rest_framework.permissions import AllowAny

from tags.models import Tag
from tags.serializers import TagSerializer


class TagViewSet(RetrieveListMixins, ModelViewSet):
    """
    ViewSet для работы с тегами.

    Атрибуты:
        queryset (QuerySet): Запрос для выборки тегов из базы данных.
        serializer_class (Serializer): Сериализатор для тегов.
        permission_classes (tuple): Кортеж с классами разрешений доступа.

    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
