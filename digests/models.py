from datetime import date

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models, transaction
from django.db.models import Prefetch, When, BooleanField, Case, F
from django.db.models.functions import (
    ExtractYear,
    ExtractMonth,
    Cast
)
from django.db.models.signals import post_save

NEWS_TYPES = {
    'txt': 'text_news',
    'img': 'image_news',
    'big': 'big_news',
    'staff': 'staff_news',
    'project': 'project_news'
}

STAFF_CARD_TYPES = {
    'accepted_to_company': 'Accepted to company',
    'passed_trial': 'Passed trial',
    'upgrade': 'Upgrade',
    'change_post': 'Change post'
}


class NewsQueryset(models.QuerySet):

    def select_related_news(self):
        queryset = (
            self
                .select_related(*NEWS_TYPES.values())
        )

        return queryset

    def get_annotated_with_favorite(self, user):
        queryset = (
            self
                .annotate(
                favorite=Case(
                    When(bookmarked_by__user=user, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
            )
        )

        return queryset


class DigestsQueryset(models.QuerySet):

    @transaction.atomic
    def bulk_create(self, objs, **kwargs):
        bulk_create_result = super().bulk_create(objs, **kwargs)
        # Triggering the signals
        for obj in objs:
            post_save.send(obj.__class__, instance=obj, created=True)
        return bulk_create_result

    def get_important_digests(self, user, value=True):

        news_queryset = (
            News.objects
                .select_related_news()
                .filter(important=value)
                .get_annotated_with_favorite(user=user)
        )
        queryset = (
            self
                .prefetch_related(Prefetch('news', queryset=news_queryset))
                .filter(news__important=value)
                .order_by('-date')
        )

        return queryset

    def get_archive_dates(self):
        """
        Returns dates of all existing digests in format [{ 'year': [list of months] }]
        Example: [
            { '2018': [2, 3, 11] },
            { '2017': [1, 5, 8] },
        ]
        :return: DigestQueryset with values('year', 'months')
        """
        aggr_months = ArrayAgg(Cast(ExtractMonth('date'), output_field=models.IntegerField()), distinct=True)
        queryset = (
            self
                .annotate(year=ExtractYear('date'))
                .values('year')
                .annotate(months=aggr_months)
                .values('year', 'months')
        )

        return queryset

    def get_published(self):
        """
        Just returns published digests.
        :return: DigestQuerySet
        """
        return self.filter(published=True)

    def prefetch_news_with_favorite(self, user, queryset=None):
        """
        Prefetching related news with annotating 'favorite' field at news.
        :param user: request.user
        :return: DigestQueryset
        """
        if not queryset:
            queryset = News.objects.all()

        queryset = (
            queryset
                .select_related_news()
                .get_annotated_with_favorite(user=user)
                .order_by('position')
        )

        return self.prefetch_related(Prefetch('news', queryset=queryset))

    def get_favorites(self, user, value=True):
        """
        Returns DigestQuerySet with favorite news.
        :param user: request.user
        :param value: favorite = True or False
        :return: DigestQueryset
        """
        news_queryset = (
            News.objects
                .select_related_news()
                .get_annotated_with_favorite(user=user)
                .filter(favorite=value)
                .order_by('position')
        )

        queryset = (
            self
                .prefetch_related(None)
                .prefetch_related(Prefetch('news', queryset=news_queryset))
                .filter(news__bookmarked_by__isnull=False)
                .filter(news__isnull=False)
                .distinct()
        )

        return queryset

    def get_unread(self, user, value=True):
        """
        Returns digests that user have read or not have read.
        :param user: request.user
        :param value: True or False
        :return: DigestQuerySet
        """
        queryset = (
            self
                .filter(unread_by__user=user)
                .filter(unread=value)
        )
        return queryset

    def get_with_unread_status(self, user):
        """
        Returns all digests with annotated field unread.
        :param user: request.user
        :return: DigestQuerySet
        """
        queryset = (
            self
                .prefetch_related('unread_by')
                .filter(unread_by__user=user)
                .annotate(unread=F('unread_by__unread'))
        )
        return queryset


class Digest(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateField(default=date.today)
    published = models.BooleanField(default=False)

    objects = DigestsQueryset.as_manager()

    def __str__(self):
        return f'{self.title}'


class News(models.Model):
    digest = models.ForeignKey(
        Digest,
        related_name='news',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=128)
    type = models.CharField(
        max_length=128,
        choices=NEWS_TYPES.items()
    )
    position = models.SmallIntegerField()
    important = models.BooleanField(default=False)

    objects = NewsQueryset.as_manager()

    @property
    def data(self):
        return getattr(self, NEWS_TYPES[self.type])

    def __str__(self):
        return f'{self.title} at {self.digest.title}'


class ImageNews(models.Model):
    news = models.OneToOneField(
        News,
        related_name='image_news',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    photo = models.URLField()

    def __str__(self):
        return f'{self.news.title}'


class TextNews(models.Model):
    news = models.OneToOneField(
        News,
        related_name='text_news',
        on_delete=models.CASCADE
    )
    content = models.TextField()

    def __str__(self):
        return f'{self.news.title}'


class BigNews(models.Model):
    news = models.OneToOneField(
        News,
        related_name='big_news',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    photo = models.URLField()

    def __str__(self):
        return f'{self.news.title}'


class StaffNews(models.Model):
    news = models.OneToOneField(
        News,
        related_name='staff_news',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.news.title}'


class Profile(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    photo = models.URLField()
    grade = models.IntegerField()
    profession = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class StaffCard(models.Model):
    staff_news = models.ForeignKey(StaffNews, related_name='staff_cards', on_delete=models.CASCADE)
    status_text = models.CharField(max_length=128)
    status_type = models.CharField(
        max_length=128,
        choices=STAFF_CARD_TYPES.items(),
        default='accepted_to_company'
    )
    project_manager = models.CharField(max_length=128, default='Без РП')

    staff_profile = models.ForeignKey(Profile, related_name='staff_card', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.staff_profile} {self.status_text}'


class ProjectNews(models.Model):
    news = models.OneToOneField(
        News,
        related_name='project_news',
        on_delete=models.CASCADE
    )

    content = models.CharField(max_length=256)
    photo = models.URLField()
    google_play = models.URLField(blank=True)
    app_store = models.URLField(blank=True)
    browser = models.URLField(blank=True)

    members = models.ManyToManyField(Profile)

    def __str__(self):
        return f'{self.news.title}'
