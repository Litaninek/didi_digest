from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'digests', views.DigestsViewset, base_name='digests')
router.register(r'news', views.NewsViewset, base_name='news')

urlpatterns = router.urls
