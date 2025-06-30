from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Article, ArticleCategory


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0
    fields = ["title", "slug", "is_published"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["view_count"]


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "article_count", "created"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ArticleInline]
    search_fields = ["name", "description"]

    def article_count(self, obj):
        return obj.articles.count()

    article_count.short_description = _("Количество")


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
    list_filter = ["category", "is_published", "published_at", "author"]
    search_fields = ["title", "content", "short_description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["view_count", "created", "modified"]
    actions = ["publish_articles", "unpublish_articles"]

    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "category")}),
        (_("Содержимое"), {"fields": ("short_description", "content", "image")}),
        (_("Публикация"), {"fields": ("is_published", "published_at")}),
        (
            _("Статистика просмотров"),
            {"fields": ("view_count",), "classes": ("collapse",)},
        ),
        (
            _("Timestamps"),
            {"fields": ("created", "modified"), "classes": ("collapse",)},
        ),
    )

    def publish_articles(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(
            request, _("Successfully published {} articles.").format(updated)
        )

    publish_articles.short_description = _("Publish selected articles")

    def unpublish_articles(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(
            request, _("Successfully unpublished {} articles.").format(updated)
        )

    unpublish_articles.short_description = _("Unpublish selected articles")
