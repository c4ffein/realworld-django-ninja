from typing import Self

import markdown
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager

User = get_user_model()


class ArticleQuerySet(models.QuerySet):
    def with_favorites(self, user: AnonymousUser | User) -> Self:
        return self.annotate(
            num_favorites=models.Count("favorites"),
            is_favorite=(
                models.Exists(get_user_model().objects.filter(pk=user.id, favorites=models.OuterRef("pk")))
                if user.is_authenticated
                else models.Value(False, output_field=models.BooleanField())
            ),
        )


ArticleManager = models.Manager.from_queryset(ArticleQuerySet)


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, unique=True, blank=False)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    tags = TaggableManager(blank=True)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="favorites")
    slug = models.SlugField(unique=True, max_length=255)  # Not a property as used for lookup

    objects = ArticleManager()

    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def as_markdown(self) -> str:
        """Unused here as we are consumed by a SPA"""
        return markdown.markdown(self.content, safe_mode="escape", extensions=["extra"])
