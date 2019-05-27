from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from digests.filters import DigestFilter
from digests.models import Digest, News
from digests.serializers import (DigestReadSerializer, DigestCreateUpdateDeleteSerializer, FullDigestSerializer,
                                 FullNewsSerializer)
from didi_digest.rest_extensions.permissions import IsAdminOrReadOnly
from users.models import UserDigests


class DigestsViewset(viewsets.ModelViewSet):
    """
    ViewSet that allows to read digests and make CRUD operations for admins.
    """
    queryset = Digest.objects.all()
    serializer_class = DigestReadSerializer
    filterset_class = DigestFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset
                .prefetch_news_with_favorite(user=self.request.user)
                .get_with_unread_status(user=self.request.user)
                .order_by('-date')
                .distinct()
        )
        # Checking if user is admin
        if not self.request.user.is_staff:
            return queryset.get_published()
        return queryset

    def _is_filtering(self):
        return any([
            self.request.query_params.get('important'),
            self.request.query_params.get('favorite'),
            self.request.query_params.get('search'),
        ])

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        # For digests/{id}/ or digests/important={true|false} we use FullDigestSerializer.
        # detailed full digest serializer
        if self.action == 'retrieve' or self._is_filtering():
            serializer_class = FullDigestSerializer
        # short digest serializer with common-user related stuff
        elif self.action == 'list':
            serializer_class = DigestReadSerializer
        # edit digest serializer for admins
        else:
            serializer_class = DigestCreateUpdateDeleteSerializer

        return serializer_class

    def retrieve(self, request, pk=None):
        requested_digest = self.get_object()
        try:
            unread_digest = request.user.digests.get(digest=requested_digest)
            unread_digest.unread = False
            unread_digest.save()
        except UserDigests.DoesNotExist:
            pass
        return super().retrieve(request, pk)

    @action(methods=['get'], detail=False)
    def date_archive(self, request):
        archive_dates = Digest.objects.all().get_archive_dates().values_list('year', 'months')
        response = {key: value for key, value in archive_dates}
        return Response(data=response, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def unread(self, request):
        user = request.user
        unread_digests_count = user.digests.filter(unread=True).count()
        data = {
            'count': unread_digests_count
        }
        return Response(data=data)


class NewsViewset(viewsets.ModelViewSet):
    queryset = News.objects.select_related()
    serializer_class = FullNewsSerializer
    permission_classes = (permissions.IsAuthenticated,)
