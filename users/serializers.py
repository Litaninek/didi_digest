from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from digests.models import News
from users.models import User, UserDigests, UserFavorite
from users.settings import EMAIL_VERIFICATION


class EmailSerialzer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('email',)

    def validate_email(self, value):
        email_vericiation_enabled = EMAIL_VERIFICATION['ENABLE_EMAIL_VERIFY']
        if email_vericiation_enabled:
            allowed_email_domain = EMAIL_VERIFICATION['ALLOWED_EMAIL_DOMAIN']
            if not value.endswith(allowed_email_domain):
                raise ValidationError('Mail domain not allowed')

        return value


class UserDigestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDigests
        fields = ('unread',)


class UserFavoritesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    news_id = serializers.PrimaryKeyRelatedField(source='news', queryset=News.objects.all())

    class Meta:
        model = UserFavorite
        fields = ('news_id', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=UserFavorite.objects.all(),
                fields=('user', 'news'),
                message='The bookmark already exists.'
            )
        ]
