import datetime

from django.urls import reverse
from django.utils import dateparse, timezone
from rest_framework import status
from rest_framework.test import APITestCase

from digests.models import Digest, News, TextNews, BigNews, ImageNews
from didi_digest.utils import reverse_with_query_params
from users.models import User


class TestDigests(APITestCase):

    def setUp(self):
        self.username = "tester"

        self.user = User.objects.create_user(
            username=self.username
        )
        self.client.force_authenticate(user=self.user)

        self.digest = Digest.objects.create(
            title='first_digest',
            date=timezone.now().date(),
            published=True,
        )
        self.digest2 = Digest.objects.create(
            title='second_digest',
            date=timezone.now().date(),
            published=True,
        )
        self.digest3 = Digest.objects.create(
            title='third_digest',
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

    def tearDown(self):
        News.objects.all().delete()
        Digest.objects.all().delete()

    def test_unread_digests(self):
        digests_count = Digest.objects.all().count()

        # Test unread digests count view
        url = reverse('digests:digests-unread')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data.get('count'), digests_count, response.data)

        # Test boolean flag at digests-list
        url = reverse('digests:digests-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['results'][0].get('unread'))
        self.assertTrue(response.data['results'][1].get('unread'))
        self.assertTrue(response.data['results'][2].get('unread'))
        # Test deleting from unread
        unread_digest_id = response.data['results'][0].get('id')
        url = reverse('digests:digests-detail', args=[unread_digest_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        url = reverse('digests:digests-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertFalse(response.data['results'][0].get('unread'))

    def create_news(self):
        url = reverse('digests:news-list')
        text_news = {
            'digest': self.digest.id,
            'title': 'Text news',
            'type': 'txt',
            'position': 1,
            'important': True,
            'data': {
                'content': 'Text content',

            }
        }

        response = self.client.post(url, data=text_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        created_news_id = response.data.get('id')
        created_news = News.objects.filter(id=created_news_id)
        self.assertTrue(created_news.exists())
        created_text_news = TextNews.objects.filter(news_id=created_news_id)
        self.assertTrue(created_text_news.exists())
        img_news = {
            'digest': self.digest2.id,
            'title': 'Image news',
            'type': 'img',
            'position': 3,
            'data': {
                'content': 'Image content',
                'photo': 'https://user.com/icon-user-default.png'

            }
        }

        response = self.client.post(url, data=img_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        big_news = {
            'digest': self.digest3.id,
            'title': 'Big news',
            'type': 'big',
            'position': 4,
            'important': True,
            'data': {
                'content': 'Image content',
                'photo': 'https://user.com/icon-user-default.png'

            }
        }

        response = self.client.post(url, data=big_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_create_digest(self):
        url = reverse('digests:digests-list')
        now = timezone.now().date()
        digest = {
            'title': 'Our new digest!',
            'published': False,
            'date': now.isoformat(),
        }
        # Acting as admin
        self.user.is_staff = True
        response = self.client.post(url, data=digest)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data.get('title'), digest.get('title'))
        self.assertEqual(dateparse.parse_date(response.data.get('date')), now)

    # Test digests news list
    def test_get_digest_list(self):
        url = reverse('digests:digests-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        results = response.data.get('results', None)
        self.assertEqual(len(results), 3, response.data)
        response_news = results[0].get('news')
        self.assertIsNotNone(response_news)
        self.assertEqual(len(response_news), 1, response_news)
        txt_news = response_news[0]
        self.assertEqual(txt_news.get('title'), self.news.title, self.news)

    def test_get_digest_detail(self):
        url = reverse('digests:news-list')
        text_news = {
            'digest': self.digest.id,
            'title': 'Text news',
            'type': 'txt',
            'position': 1,
            'important': True,
            'data': {
                'content': 'Text content',

            }
        }

        response = self.client.post(url, data=text_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        created_news_id = response.data.get('id')
        created_news = News.objects.filter(id=created_news_id)
        self.assertTrue(created_news.exists())
        created_text_news = TextNews.objects.filter(news_id=created_news_id)
        self.assertTrue(created_text_news.exists())
        img_news = {
            'digest': self.digest.id,
            'title': 'Image news',
            'type': 'img',
            'position': 3,
            'data': {
                'content': 'Image content',
                'photo': 'https://user.com/icon-user-default.png'

            }
        }

        response = self.client.post(url, data=img_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        big_news = {
            'digest': self.digest.id,
            'title': 'Big news',
            'type': 'big',
            'position': 4,
            'data': {
                'content': 'Image content',
                'photo': 'https://user.com/icon-user-default.png'

            }
        }

        response = self.client.post(url, data=big_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        url = reverse('digests:digests-detail', args=[self.digest.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data.get('id'), self.digest.id)
        self.assertEqual(response.data.get('title'), self.digest.title)
        response_news = response.data.get('news')
        self.assertIsNotNone(response_news)
        self.assertEqual(len(response_news), 4, response_news)
        txt_news = response_news[-1]
        self.assertEqual(txt_news.get('title'), self.news.title, self.news)

    def test_get_digest_not_found(self):
        url = reverse('digests:news-detail', args=[-1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_delete_digests(self):
        # Acting as admin
        self.user.is_staff = True
        url = reverse('digests:digests-detail', args=[self.digest.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_filter_important(self):
        self.create_news()
        query_params = {'important': True}
        url = reverse_with_query_params('digests:digests-list', query_params)
        response = self.client.get(url)
        self.assertEqual(len(response.data.get('results')), 2)
        self.assertEqual(len(response.data.get('results')[0]['news']), 1)
        self.assertEqual(response.data.get('results')[0]['news'][0]['important'], True)
        self.assertEqual(len(response.data.get('results')[1]['news']), 1)
        self.assertEqual(response.data.get('results')[1]['news'][0]['important'], True)

    def test_filter_dates(self):
        Digest.objects.all().delete()
        # Using bulk_create doesn't trigger signal post_save
        Digest.objects.bulk_create([
            Digest(title='2018-01-01', date='2018-01-01', published=True),
            Digest(title='2018-01-02', date='2018-01-02', published=True),
            Digest(title='2018-01-02', date='2018-02-02', published=True),
            Digest(title='2018-02-02', date='2018-02-02', published=True),
            Digest(title='2017-01-01', date='2017-01-01', published=True)
        ])
        digests_testing_url = 'digests:digests-list'
        query_params = {'year': 2018, 'month': 1}
        url = reverse_with_query_params(digests_testing_url, query_params)
        response = self.client.get(url)
        self.assertEqual(response.data.get('count'), 2, response.data)
        query_params = {'year': 2018, 'month': 2}
        url = reverse_with_query_params(digests_testing_url, query_params)
        response = self.client.get(url)
        self.assertEqual(response.data.get('count'), 2, response.data)
        query_params = {'year': 2018}
        url = reverse_with_query_params(digests_testing_url, query_params)
        response = self.client.get(url)
        self.assertEqual(response.data.get('count'), 4, response.data)
        query_params = {'year': 2017}
        url = reverse_with_query_params(digests_testing_url, query_params)
        response = self.client.get(url)
        self.assertEqual(response.data.get('count'), 1)
        query_params = {'year': 2017, 'month': 1}
        url = reverse_with_query_params(digests_testing_url, query_params)
        response = self.client.get(url)
        self.assertEqual(response.data.get('count'), 1)
        query_params = {'year': 2016, 'month': 1}
        url = reverse_with_query_params(digests_testing_url, query_params)
        response = self.client.get(url)
        self.assertEqual(response.data.get('count'), 0)

    def test_get_dates(self):
        Digest.objects.all().delete()
        Digest.objects.bulk_create([
            Digest(title='2018-01-01', date='2018-01-01', published=True),
            Digest(title='2018-01-02', date='2018-01-02', published=True),
            Digest(title='2018-01-02', date='2018-02-02', published=True),
            Digest(title='2018-02-02', date='2018-02-02', published=True),
            Digest(title='2017-01-01', date='2017-01-01', published=True)
        ])
        url = reverse('digests:digests-date-archive')
        response = self.client.get(url)
        self.assertEqual(len(response.data.get(2017)), 1, response.data)
        self.assertEqual(response.data.get(2017), [1], response.data)
        self.assertEqual(len(response.data.get(2018)), 2, response.data)
        self.assertEqual(response.data.get(2018), [1, 2], response.data)


class TestNews(APITestCase):

    def setUp(self):
        self.digest = Digest.objects.create(
            title='first_digest',
            date=datetime.date.today(),
        )

        self.username = "tester"
        self.password = "testing"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.client.force_authenticate(user=self.user)

    # POST News block
    def create_digest_news(self):
        url = reverse('digests:news-list')
        text_news = {
            'digest': self.digest.id,
            'title': 'Text news',
            'type': 'txt',
            'position': 1,
            'data': {
                'content': 'Text content',

            }
        }

        response = self.client.post(url, data=text_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        created_news_id = response.data.get('id')
        created_news = News.objects.filter(id=created_news_id)
        self.assertTrue(created_news.exists())
        created_text_news = TextNews.objects.filter(news_id=created_news_id)
        self.assertTrue(created_text_news.exists())
        img_news = {
            'digest': self.digest.id,
            'title': 'Image news',
            'type': 'img',
            'position': 3,
            'data': {
                'content': 'Image content',
                'photo': 'https://user.com/icon-user-default.png'

            }
        }

        response = self.client.post(url, data=img_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        big_news = {
            'digest': self.digest.id,
            'title': 'Big news',
            'type': 'big',
            'position': 4,
            'data': {
                'content': 'Image content',
                'photo': 'https://user.com/icon-user-default.png'

            }
        }

        response = self.client.post(url, data=big_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    # DELETE News block
    def test_delete_news(self):
        url = reverse('digests:news-list')
        text_news = {
            'digest': self.digest.id,
            'title': 'Text news',
            'type': 'txt',
            'position': 1,
            'data': {
                'content': 'Text content',

            }
        }
        response = self.client.post(url, data=text_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        news_id = response.data.get('id')
        url = reverse('digests:news-detail', args=[news_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    # PATCH News block
    def test_patch_news(self):
        url = reverse('digests:news-list')
        text_news = {
            'digest': self.digest.id,
            'title': 'Text news',
            'type': 'txt',
            'position': 1,
            'data': {
                'content': 'Text content',

            }
        }
        response = self.client.post(url, data=text_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        news_id = response.data.get('id')
        url = reverse('digests:news-detail', args=[news_id])
        patched_data = {
            'title': 'patched title',
            'data': {
                'content': 'patched_content'
            }
        }
        response = self.client.patch(url, data=patched_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(
            response.data.get('data').get('content'),
            patched_data.get('data').get('content'),
            response.data
        )
        self.assertEqual(response.data.get('title'), patched_data.get('title'), response.data)

    def test_change_type_forbidden(self):
        url = reverse('digests:news-list')
        text_news = {
            'digest': self.digest.id,
            'title': 'Text news',
            'type': 'txt',
            'position': 1,
            'data': {
                'content': 'Text content',

            }
        }
        response = self.client.post(url, data=text_news, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        news_id = response.data.get('id')
        url = reverse('digests:news-detail', args=[news_id])
        patched_data = {
            'title': 'patched title',
            'type': 'img',
            'data': {
                'content': 'patched_content'
            }
        }
        response = self.client.patch(url, data=patched_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)


class TestFullTextSearch(APITestCase):

    def setUp(self):
        main_digest = Digest.objects.create(
            title='Новостной дайджест SML',
            date=timezone.now().date(),
            published=True,
        )

        main_news = News.objects.bulk_create(
            News(
                digest=main_digest,
                title='Апрельская активность SML',
                position=1,
                type='big',
                important=True
            ),
            News(
                digest=main_digest,
                title='Первый футбольный матч SML',
                position=2,
                type='img',
                important=False
            ),
            News(
                digest=main_digest,
                title='Про отдых в мае',
                position=3,
                type='txt',
                important=True
            )
        )

        big_news = BigNews(
            news=main_news[0],
            content="""
            Уже в эту субботу, 28 апреля, в офисе состоится мероприятие, посвященное Actions on Google. 
            В рамках митапа мы будем создавать Actions для Google Assistant в той тематике, которая интересна именно вам. 
            Мероприятие будет полезно для разработчиков всех уровней. А поможет нам в этом разобраться Google Developer Experts Алексей Коровянский (GDE Omsk) и Avi Ashkenazi (GDE, London).

            Программа             
            11:30 - сбор участников
            12:10 - Designing for voice interfaces. Avi Ashkenazi (GDE, London, UK)
            13:00 - кофе-брейк и обсуждение идей
            15:00 - разработка собственного проекта
            17:30 - заполнение формы фидбека
            15:00 - разработка собственного проекта
            """
        )

    def test_full_text_search(self):
        query_params = {
            'search': 'Testing full text search'
        }
        url = reverse_with_query_params('digests:digests-list', query_params)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data.get('results')), 1, response.data)
        self.assertIsNotNone(response.data.get('results')[0].get('news'), response.data)
        self.assertEqual(response.data.get('results').get('news')[0].get('id'), self.main_news[0].id, response.data)
        self.assertEqual(response.data.get('results'))
        digest = response.data.get('results')[0]
        self.assertEqual()
