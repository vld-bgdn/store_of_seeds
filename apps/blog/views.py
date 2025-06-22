from django.views.generic import ListView, DetailView
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404

from .models import Article, ArticleCategory


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return (
            Article.objects.filter(is_published=True)
            .select_related("author", "category")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ArticleCategory.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True))
        ).filter(article_count__gt=0)

        popular_articles = Article.objects.filter(is_published=True).order_by("-view_count")[:5]

        context["popular_articles"] = popular_articles
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related(
            "author", "category"
        )

    def get_object(self, queryset=None):
        """Get object and increment view count"""
        obj = super().get_object(queryset)
        # Increment view count using F() to avoid race conditions
        Article.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        # Refresh the object to get updated view_count
        obj.refresh_from_db(fields=["view_count"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        # Get related articles from same category first, then others
        related_articles = Article.objects.filter(is_published=True).exclude(
            id=article.id
        )
        if article.category:
            related_articles = related_articles.filter(category=article.category)
        context["related_articles"] = related_articles[:4]

        context["categories"] = ArticleCategory.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True))
        ).filter(article_count__gt=0)

        return context


class CategoryArticleListView(ListView):
    model = Article
    template_name = "blog/category_article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return (
            Article.objects.filter(
                category__slug=self.kwargs["slug"], is_published=True
            )
            .select_related("author", "category")
            .order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            ArticleCategory, slug=self.kwargs["slug"]
        )
        context["categories"] = ArticleCategory.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_published=True))
        ).filter(article_count__gt=0)
        return context
