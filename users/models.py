from django.contrib.auth.models import AbstractUser
from django.db import models

from digests.models import Digest, News


class User(AbstractUser):
    pass


class UserDigests(models.Model):
    user = models.ForeignKey(User, related_name='digests', on_delete=models.CASCADE)
    digest = models.ForeignKey(Digest, related_name='unread_by', on_delete=models.CASCADE)
    unread = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'digest')

    def __str__(self):
        return f"<{self.user.__str__()} x {self.digest.title}>"


class UserFavorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    news = models.ForeignKey(News, related_name='bookmarked_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'news')

    def __str__(self):
        return f"<{self.user.__str__()} <3 {self.news.title}>"
