from rest_framework import permissions, viewsets

from didi_digest.rest_extensions.permissions import IsOwnerOnly
from users.models import UserFavorite
from users.serializers import UserFavoritesSerializer


class UserFavoritesViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsOwnerOnly)
    serializer_class = UserFavoritesSerializer
    queryset = UserFavorite.objects.all()
    http_method_names = ['get', 'post', 'head', 'delete', 'options']
    lookup_field = 'news_id'

    def get_queryset(self):
        """
        Actually returns favorites that belong to current user.
        :return: UserFavoriteQuerySet
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
