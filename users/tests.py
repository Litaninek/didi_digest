from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from digests.models import News, Digest, TextNews
from didi_digest.utils import reverse_with_query_params
from users.models import User


class TestFavorite(APITestCase):

    def setUp(self):
        self.username = "tester"

        self.user = User.objects.create_user(
            username=self.username
        )
        self.digest = Digest.objects.create(
            title='first_digest',
            date=timezone.now().date(),
            published=True,
        )
        self.news = News.objects.create(
            title='first digest news',
            digest=self.digest,
            position=1,
            important=False,
            type='txt',
        )
        self.text_news = TextNews(
            content="test content",
            news=self.news
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        News.objects.all().delete()
        Digest.objects.all().delete()

    def _create_favorite(self, news_id):
        url = reverse('users:favorites-list')
        data = {
            'news_id': news_id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        return response

    def test_create_favorite(self):
        url = reverse('users:favorites-list')
        data = {
            'news_id': self.news.id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data.get('news'), data.get('news'), response.data)

    def test_get_favorites(self):
        url = reverse('users:favorites-list')
        data = {
            'news_id': self.news.id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data.get('news'), data.get('news'), response.data)
        url = reverse('users:favorites-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_forbidden_get_favorite_by_not_creator(self):
        url = reverse('users:favorites-list')
        data = {
            'news_id': self.news.id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data.get('news'), data.get('news'), response.data)
        favorite_id = response.data.get('news_id')
        not_creator = User.objects.create_user(
            username='not_creator'
        )
        self.client.force_authenticate(user=not_creator)
        url = reverse('users:favorites-detail', args=[favorite_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_delete_favorite(self):
        url = reverse('users:favorites-list')
        data = {
            'news_id': self.news.id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data.get('news'), data.get('news'), response.data)
        favorite_id = response.data.get('news_id')
        url = reverse('users:favorites-detail', args=[favorite_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_forbidden_delete_favorite_by_not_creator(self):
        url = reverse('users:favorites-list')
        data = {
            'news_id': self.news.id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data.get('news'), data.get('news'), response.data)
        favorite_id = response.data.get('news_id')
        not_creator = User.objects.create_user(
            username='not_creator'
        )
        self.client.force_authenticate(user=not_creator)
        url = reverse('users:favorites-detail', args=[favorite_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_get_filtered_favorite_news(self):
        news_list_to_add = [
            News(title='news_1', digest=self.digest, type='txt', position=2),
            News(title='news_2', digest=self.digest, type='txt', position=3),
            News(title='news_3', digest=self.digest, type='txt', position=4),
            News(title='news_4', digest=self.digest, type='txt', position=5)
        ]
        News.objects.bulk_create(news_list_to_add)
        favorite = self._create_favorite(self.news.id).data
        favorite_news_id = favorite.get('news_id')
        query_params = {
            'favorite': True
        }

        url = reverse_with_query_params('digests:digests-list', query_params=query_params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data.get('count'), 1, response.data)
        self.assertEqual(len(response.data.get('results')[0].get('news')), 1, response.data)
        self.assertEqual(response.data.get('results')[0].get('news')[0].get('id'), favorite_news_id, response.data)
        new_favorite = self._create_favorite(news_id=news_list_to_add[0].id).data
        new_favorite_id = new_favorite.get('news')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data.get('results')[0].get('news')), 2, response.data)
        self.assertEqual(response.data.get('results')[0].get('news')[1].get('news_id'), new_favorite_id, response.data)
