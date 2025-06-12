from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Article, ArticleCategory


class ArticleInline(admin.StackedInline):
    model = Article
    extra = 0
    fields = ["title", "slug", "is_published"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "article_count"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ArticleInline]

    def article_count(self, obj):
        return obj.article_set.count()

    article_count.short_description = _("Articles")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "author",
        "is_published",
        "published_at",
        "view_count",
    ]
    list_filter = ["category", "is_published", "published_at"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["view_count", "created", "modified"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "author",
                    "image",
                    "short_description",
                    "content",
                )
            },
        ),
        (_("Publication"), {"fields": ("is_published", "published_at")}),
        (_("Statistics"), {"fields": ("view_count", "created", "modified")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
