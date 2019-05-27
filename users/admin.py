from django.contrib import admin
from users.models import UserDigests, UserFavorite, User

admin.site.register(UserDigests)
admin.site.register(UserFavorite)
admin.site.register(User)
