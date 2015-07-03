from django.conf import settings
from django.db import models
from django.utils import timezone

from jsonfield import JSONField


class Person(models.Model):
    email = models.EmailField(unique=True, blank=True, null=True)
    source = models.CharField(max_length=64)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=128, blank=True)
    twitter_id = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True)
    blog = models.URLField(blank=True)
    hireable = models.NullBooleanField()
    company = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    tags = JSONField(blank=True)

    class Meta:
        ordering = ['-updated',]
        verbose_name_plural = "people"
