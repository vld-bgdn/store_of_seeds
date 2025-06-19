from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django_ckeditor_5.fields import CKEditor5Field


class ArticleCategory(TimeStampedModel):
    """Category for blog articles"""

    name = models.CharField(_("Название"), max_length=100)
    slug = models.SlugField(_("Псведоним"), max_length=100, unique=True)
    description = models.TextField(_("Описание"), blank=True)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category_article_list", kwargs={"slug": self.slug})


class Article(TimeStampedModel):
    """Blog article model"""

    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("Псведоним"), max_length=200, unique=True)
    author = models.ForeignKey(
        User,
        verbose_name=_("Автор"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        ArticleCategory,
        verbose_name=_("Категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",  # This allows reverse lookup
    )
    content = CKEditor5Field(_("Контент"), config_name="extends")
    short_description = models.TextField(_("Короткое описание"), blank=True)
    is_published = models.BooleanField(_("Опубликовано"), default=False)
    published_at = models.DateTimeField(_("Время публикации"), blank=True, null=True)
    image = models.ImageField(_("image"), upload_to="articles/", blank=True)
    view_count = models.PositiveIntegerField(_("Количество просмотров"), default=0)

    class Meta:
        verbose_name = _("Статья")
        verbose_name_plural = _("Статьи")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:article_detail", kwargs={"slug": self.slug})

    def increment_view_count(self):
        """Increment view count safely"""
        self.view_count += 1
        self.save(update_fields=["view_count"])
