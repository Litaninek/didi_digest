from django.contrib import admin
from .models import (
    News,
    TextNews,
    ImageNews,
    BigNews,
    Digest,
    StaffNews,
    StaffCard,
    ProjectNews,
    Profile
)


class Choice3Inline(admin.TabularInline):
    model = Profile
    extra = 1


class Choice2Inline(admin.TabularInline):
    model = StaffCard
    extra = 1
    #   inlines = [Choice3Inline]


class ChoiceInline(admin.TabularInline):
    model = News
    extra = 1


class DigestAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'published')
    fieldsets = [
        (None, {'fields': ['title', 'published']}),
        ('Date information', {'fields': ['date', ], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]


class Admin(admin.ModelAdmin):
    inlines = [Choice2Inline]


admin.site.register(News)
admin.site.register(Digest, DigestAdmin)
admin.site.register(TextNews)
admin.site.register(ImageNews)
admin.site.register(BigNews)
admin.site.register(StaffNews, Admin)
admin.site.register(ProjectNews)
admin.site.register(StaffCard)
admin.site.register(Profile)
