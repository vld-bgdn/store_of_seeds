from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Category(TimeStampedModel):
    """Category model for product classification (2-level hierarchy)"""

    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent category"),
        related_name="children",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    description = models.TextField(_("description"), blank=True)
    image = models.ImageField(_("image"), upload_to="categories/", blank=True)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """Product model for microgreens seeds and equipment"""

    class DifficultyLevel(models.TextChoices):
        EASY = "easy", _("Easy")
        MEDIUM = "medium", _("Medium")
        HARD = "hard", _("Hard")

    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    article = models.CharField(_("article"), max_length=50, unique=True)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        _("old price"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    short_description = models.TextField(_("short description"), blank=True)
    full_description = models.TextField(_("full description"), blank=True)
    stock = models.PositiveIntegerField(_("stock"), default=0)
    is_active = models.BooleanField(_("is active"), default=True)

    # Seed-specific fields
    germination_time = models.CharField(
        _("germination time"), max_length=50, blank=True
    )
    difficulty_level = models.CharField(
        _("difficulty level"),
        max_length=10,
        choices=DifficultyLevel.choices,
        blank=True,
    )
    taste_characteristics = models.TextField(_("taste characteristics"), blank=True)
    benefits = models.TextField(_("benefits"), blank=True)
    recommended_substrate = models.CharField(
        _("recommended substrate"), max_length=100, blank=True
    )
    growing_instructions = models.TextField(_("growing instructions"), blank=True)
    recommended_temperature = models.CharField(
        _("recommended temperature"), max_length=50, blank=True
    )
    harvest_dates = models.CharField(_("harvest dates"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductImage(TimeStampedModel):
    """Model for product images"""

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(_("image"), upload_to="products/")
    is_main = models.BooleanField(_("is main"), default=False)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} - Image {self.pk}"
