from rest_framework import routers

from . import views

router = routers.SimpleRouter()

router.register(r'favorites', views.UserFavoritesViewset, base_name='favorites')

urlpatterns = router.urls
