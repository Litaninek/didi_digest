from django.db.models.signals import post_save
from django.dispatch import receiver

from digests.models import Digest
from users.models import User, UserDigests


@receiver(post_save, sender=Digest)
def add_to_unread_by_users(sender, instance, **kwargs):
    """
    This signals handles adding digest to unread digests by all users when digest is created
    :param sender: Digest model
    :param instance: Digest instance
    :param kwargs: dict
    :return:
    """
    if instance.published:
        all_users = User.objects.all()
        all_unread = [
            UserDigests(user=user, digest=instance, unread=True)
            for user in all_users.iterator()
            if not user.digests.filter(digest=instance)
        ]
        UserDigests.objects.bulk_create(all_unread)
