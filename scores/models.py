from django.db import models
from django.conf import settings


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Score(models.Model):
    name = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255, blank=True, default='')
    groups = models.ManyToManyField(Group, blank=True, related_name='scores')
    file = models.FileField(upload_to='scores/')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
