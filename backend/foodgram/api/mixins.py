from django.shortcuts import get_object_or_404
from rest_framework import  mixins, viewsets
from rest_framework.response import Response
from rest_framework import status

class ListCreateRetrieveMixins(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    pass

class CreateOrDeleteMixins(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
     
      def create(self, request, id):
    
        serializer = self.get_serializer(id)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

      def delete(self, request, id):

        obj = get_object_or_404(self.model_class, id=id)
        queryset = self.get_queryset()

        if queryset.filter(id=id):
            queryset.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': f'{self.error}', },
            status=status.HTTP_400_BAD_REQUEST
        )