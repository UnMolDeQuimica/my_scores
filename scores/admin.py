from django.contrib import admin
from .models import Score, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'owner', 'created_at')
    list_filter = ('groups', 'owner')
    search_fields = ('name', 'author')
    filter_horizontal = ('groups',)
