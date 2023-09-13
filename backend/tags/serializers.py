from rest_framework import serializers

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.

    Атрибуты:
        model (Model): Модель, с которой связан сериализатор.
        fields (list): Список полей, которые должны быть сериализованы.

    """
    class Meta:
        model = Tag
        fields = ('__all__')


class TagField(serializers.SlugRelatedField):
    """
    Пользовательский поле для сериализации связанных тегов.

    Методы:
        to_representation(value): Переопределенный метод для сериализации тегов.

    """
    def to_representation(self, value):
        """
        Сериализует связанный тег.

        Args:
            value: Объект тега.

        Returns:
            dict: Сериализованный объект тега.

        """
        request = self.context.get('request')
        context = {'request': request}
        serializer = TagSerializer(value, context=context)
        return serializer.data