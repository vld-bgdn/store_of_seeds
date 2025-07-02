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
        EASY = "easy", _("легкая")
        MEDIUM = "medium", _("средняя")
        HARD = "hard", _("сложная")

    category = models.ForeignKey(
        Category,
        verbose_name=_("категория"),
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField(_("название"), max_length=200)
    slug = models.SlugField(_("псевдоним"), max_length=200, unique=True)
    article = models.CharField(_("артикул"), max_length=50, unique=True)
    price = models.DecimalField(_("цена"), max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        _("старая цена"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    short_description = models.TextField(_("короткое описание"), blank=True)
    full_description = models.TextField(_("полное описание"), blank=True)
    stock = models.PositiveIntegerField(_("остаток"), default=0)
    is_active = models.BooleanField(_("активно"), default=True)

    # Seed-specific fields
    germination_time = models.CharField(
        _("время проростания"), max_length=50, blank=True
    )
    difficulty_level = models.CharField(
        _("сложность выращивания"),
        max_length=10,
        choices=DifficultyLevel.choices,
        blank=True,
    )
    taste_characteristics = models.TextField(_("вкусовые характеристики"), blank=True)
    benefits = models.TextField(_("полезные свойства"), blank=True)
    recommended_substrate = models.CharField(
        _("рекомендуемый субстрат"), max_length=100, blank=True
    )
    growing_instructions = models.TextField(_("инструкция по проращиванию"), blank=True)
    recommended_temperature = models.CharField(
        _("рекомендуемая температура"), max_length=50, blank=True
    )
    harvest_dates = models.CharField(_("дата сбора"), max_length=100, blank=True)

    @property
    def is_microgreens(self):
        return self.category.slug == "microgreens-seeds" or (
            self.category.parent and self.category.parent.slug == "microgreens-seeds"
        )

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
        verbose_name=_("продукт"),
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(_("изображение"), upload_to="products/")
    is_main = models.BooleanField(_("основное"), default=False)
    order = models.PositiveIntegerField(_("заказ"), default=0)

    class Meta:
        verbose_name = _("изображение продукта")
        verbose_name_plural = _("изображения продукта")
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} - Image {self.pk}"
