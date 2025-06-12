from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Page(TimeStampedModel):
    """Static page model"""

    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    content = models.TextField(_("content"))
    is_active = models.BooleanField(_("is active"), default=True)
    meta_title = models.CharField(_("meta title"), max_length=200, blank=True)
    meta_description = models.TextField(_("meta description"), blank=True)
    template_name = models.CharField(
        _("template name"), max_length=100, default="pages/default.html"
    )

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ["title"]

    def __str__(self):
        return self.title
