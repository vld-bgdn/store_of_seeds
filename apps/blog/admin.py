from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# from .models import Article, ArticleCategory
from .models import Article


class ArticleInline(admin.StackedInline):
    model = Article
    extra = 0
    fields = ["title", "slug", "is_published"]
    prepopulated_fields = {"slug": ("title",)}


# @admin.register(ArticleCategory)
# class ArticleCategoryAdmin(admin.ModelAdmin):
#     list_display = ["name", "slug", "article_count"]
#     prepopulated_fields = {"slug": ("name",)}
#     inlines = [ArticleInline]

#     def article_count(self, obj):
#         return obj.article_set.count()

#     article_count.short_description = _("Articles")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        # "category",
        "author",
        "is_published",
        "published_at",
        # "view_count",
    ]
    # list_filter = ["category", "is_published", "published_at"]
    list_filter = ["is_published", "published_at"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    # readonly_fields = ["view_count", "created", "modified"]
    readonly_fields = ["created", "modified"]
    actions = ["publish_articles", "unpublish_articles"]  # List of action names

    def publish_articles(self, request, queryset):
        queryset.update(is_published=True)

    publish_articles.short_description = _("Publish selected articles")

    def unpublish_articles(self, request, queryset):
        queryset.update(is_published=False)

    unpublish_articles.short_description = _("Unpublish selected articles")
