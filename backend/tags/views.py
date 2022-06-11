from recipes.mixins import RetrieveListMixins
from rest_framework.permissions import AllowAny

from tags.models import Tag
from tags.serializers import TagSerializer


class TagViewSet(RetrieveListMixins):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
