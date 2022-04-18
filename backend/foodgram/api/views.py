from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Exists, OuterRef
from .serializers import CustomUserSerializer, FollowSerializer, ResetPasswordSerializer
#from djoser.views import UserViewSet as DjoserViewSet
from .mixins import ListCreateRetrieveViewSets
from users.models import User


class UserViewSet(ListCreateRetrieveViewSets):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'list' or 'create':
            return (AllowAny,)
        return IsAuthenticated

    def get_serializer_class(self):
        if self.action == 'set_password':
            return ResetPasswordSerializer
        if self.action == 'subscriptions':
            return  FollowSerializer
        return CustomUserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            subscriptions = user.following.filter(id=OuterRef('id'))
            return User.objects.annotate(is_subscribed=Exists(subscriptions))
        return User.objects.all()

    @action(methods=('GET'), detail=False, url_path='me')
    def me(self, request):
        user = request.user 
        serializer = self.get_serializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=('GET'), detail=False, url_path='subscriptions')

    



   
