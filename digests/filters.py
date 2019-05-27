from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Prefetch, Q
from django_filters import rest_framework as filters

from .models import Digest, News


class DigestFilter(filters.FilterSet):
    important = filters.BooleanFilter(method='filter_important')
    favorite = filters.BooleanFilter(method='filter_favorite')
    unread = filters.BooleanFilter(method='filter_unread')
    search = filters.CharFilter(method='search_filter')
    year = filters.NumberFilter(field_name='date', lookup_expr='year')
    month = filters.NumberFilter(field_name='date', lookup_expr='month')
    day = filters.NumberFilter(field_name='date', lookup_expr='day')

    class Meta:
        model = Digest
        fields = ('important', 'search', 'favorite')

    def filter_important(self, queryset, name, value):
        queryset = queryset.prefetch_related(None)
        return queryset.get_important_digests(user=self.request.user)

    def filter_favorite(self, queryset, name, value):
        return queryset.get_favorites(user=self.request.user)

    def filter_unread(self, queryset, name, value):
        return queryset.get_unread(user=self.request.user)

    def search_filter(self, queryset, name, value):
        search_string = value
        news_queryset = (
            News
                .objects.select_related_news()
                .prefetch_related(
                Prefetch('text_news'),
                Prefetch('big_news'),
                Prefetch('image_news'))
                .all()
        )
        filtered_news = news_queryset.filter(
            Q(text_news__isnull=False) |
            Q(image_news__isnull=False) |
            Q(big_news__isnull=False)
        )

        filtered_news = (
            filtered_news
                .prefetch_related(
                Prefetch('text_news'),
                Prefetch('big_news', ),
                Prefetch('image_news', ))
        )

        news_queryset = (
            filtered_news
                .all()
                .annotate(
                search=SearchVector('text_news__content', 'title') +
                       SearchVector('image_news__content') +
                       SearchVector('big_news__content')
            )
                .filter(search=SearchQuery(search_string))
        )

        queryset = (
            Digest.objects.all()
                .prefetch_news_with_favorite(user=self.request.user, queryset=news_queryset)
        )

        queryset = (
            queryset
                .get_with_unread_status(user=self.request.user)
                .filter(news__in=news_queryset.values('id'))
                .distinct()
        )
        return queryset
