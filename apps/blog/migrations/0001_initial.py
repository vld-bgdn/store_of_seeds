# Generated by Django 5.2 on 2025-06-12 14:01

import django.db.models.deletion
import django.utils.timezone
import django_ckeditor_5.fields
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticleCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="name")),
                (
                    "slug",
                    models.SlugField(max_length=100, unique=True, verbose_name="slug"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
            ],
            options={
                "verbose_name": "article category",
                "verbose_name_plural": "article categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="title")),
                (
                    "slug",
                    models.SlugField(max_length=200, unique=True, verbose_name="slug"),
                ),
                (
                    "content",
                    django_ckeditor_5.fields.CKEditor5Field(verbose_name="content"),
                ),
                (
                    "short_description",
                    models.TextField(blank=True, verbose_name="short description"),
                ),
                (
                    "is_published",
                    models.BooleanField(default=False, verbose_name="is published"),
                ),
                (
                    "published_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="published at"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, upload_to="articles/", verbose_name="image"
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="author",
                    ),
                ),
            ],
            options={
                "verbose_name": "article",
                "verbose_name_plural": "articles",
                "ordering": ["-published_at"],
            },
        ),
    ]
