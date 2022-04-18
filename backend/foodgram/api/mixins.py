from rest_framework import  mixins, viewsets

class ListCreateRetrieveViewSets(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    pass