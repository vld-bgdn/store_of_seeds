from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "is_active")}),
        (_("SEO"), {"fields": ("meta_title", "meta_description")}),
        (_("Advanced"), {"fields": ("template_name",), "classes": ("collapse",)}),
    )
