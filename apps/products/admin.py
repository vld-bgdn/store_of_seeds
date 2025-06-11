from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "article", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {"fields": ("category", "name", "slug", "article", "is_active")}),
        ("Цена и наличие", {"fields": ("price", "old_price", "stock")}),
        ("Описание", {"fields": ("short_description", "full_description")}),
        (
            "Характеристики семян",
            {
                "fields": (
                    "germination_time",
                    "difficulty_level",
                    "taste_characteristics",
                    "benefits",
                    "recommended_substrate",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Инструкция по выращиванию",
            {
                "fields": (
                    "growing_instructions",
                    "recommended_temperature",
                    "harvest_dates",
                ),
                "classes": ("collapse",),
            },
        ),
    )
