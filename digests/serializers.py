from django.db import models, transaction
from rest_framework import serializers

from digests.models import (
    BigNews,
    Digest,
    ImageNews,
    News,
    TextNews,
    StaffNews,
    StaffCard,
    ProjectNews
)


class ProjectNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectNews
        fields = (
            'content',
            'photo',
            'google_play',
            'app_store',
            'browser',
            'members'
        )
        depth = 1


class StaffCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffCard
        fields = (
            'id',
            'project_manager',
            'status_type',
            'status_text',
            'staff_profile',
        )
        depth = 2


class StaffNewsSerializer(serializers.ModelSerializer):
    staff_cards = StaffCardSerializer(many=True)

    class Meta:
        model = StaffNews
        fields = ('staff_cards',)
        depth = 2


class TextNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextNews
        exclude = ('id', 'news')


class ImageNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageNews
        exclude = ('id', 'news')


class BigNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigNews
        exclude = ('id', 'news')


class NewsSerializer(serializers.ModelSerializer):
    # Annotated field
    favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = News
        fields = ('id', 'title', 'type', 'important', 'position',
                  # annotated in queryset
                  'favorite')


class FullNewsListSerializer(serializers.ListSerializer):
    """
    List Serializer that builds each item of the list and creates list of items with different fields.
    By default it was building serializer class only one time and making a list of items with same fields
    """

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        iterable = data.all() if isinstance(data, models.Manager) else data
        child_class = self.child.__class__
        return [
            child_class(instance=item, context=self.child.context).to_representation(item) for item in iterable
        ]


class DigestCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    news = NewsSerializer(many=True, read_only=True)

    class Meta:
        model = Digest
        fields = ('id', 'title', 'date', 'news')
        extra_kwargs = {
            'date': {
                'required': True
            },
        }


class DigestReadSerializer(serializers.ModelSerializer):
    news = NewsSerializer(many=True, read_only=True)
    # Annotated field
    unread = serializers.SerializerMethodField()

    class Meta:
        model = Digest
        fields = ('id', 'title', 'date', 'news',
                  # annotated in queryset
                  'unread')
        extra_kwargs = {
            'date': {
                'required': True
            },
        }

    def get_unread(self, obj):
        return obj.unread


class FullNewsSerializer(NewsSerializer):
    # Annotated field
    favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = News
        fields = ('id', 'digest', 'title',
                  'type', 'important', 'position',
                  # Annotated field
                  'favorite')
        list_serializer_class = FullNewsListSerializer

        # Mapping for declaring serializer fields to specific news.
        type_mapping = {
            'txt': TextNewsSerializer,
            'img': ImageNewsSerializer,
            'big': BigNewsSerializer,
            'staff': StaffNewsSerializer,
            'project': ProjectNewsSerializer,
        }

    def validate_type(self, value):
        if hasattr(self.instance, 'type') and value != self.instance.type:
            msg = "you can't change type"
            raise serializers.ValidationError(msg)
        return value

    def get_fields(self):
        fields = super().get_fields()
        news_type = getattr(self.instance, 'type', None) or getattr(self, 'initial_data', {}).get('type')
        is_create = hasattr(self, 'initial_data') and not getattr(self, 'instance', None)
        if is_create:
            try:
                news_type = self.initial_data.get('type')
                news_type = fields['type'].to_internal_value(data=news_type)
            except serializers.ValidationError as e:
                msg = e.detail
                raise serializers.ValidationError({'type': msg})

        fields['data'] = self.Meta.type_mapping.get(news_type)(required=True)

        return fields

    @transaction.atomic
    def create(self, validated_data):
        data = validated_data.pop('data')
        news = super().create(validated_data)
        data.update({'news': news})
        serialzier = self.fields['data']
        serialzier.create(validated_data=data)
        return news

    @transaction.atomic
    def update(self, instance, validated_data):
        data = validated_data.pop('data')
        instance = super().update(instance, validated_data)
        serialzier = self.fields['data']
        serialzier.update(instance=instance.data, validated_data=data)
        return instance


class FullDigestSerializer(serializers.ModelSerializer):
    news = FullNewsSerializer(many=True)

    class Meta:
        model = Digest
        fields = ('id', 'title', 'date', 'news')
