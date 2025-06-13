from django.views.generic import ListView, DetailView
from django.db.models import Count

# from .models import Article, ArticleCategory
from .models import Article


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return (
            Article.objects.filter(is_published=True)
            # .select_related("author", "category")
            .select_related("author").order_by("-published_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["categories"] = ArticleCategory.objects.annotate(
        #     article_count=Count("article")
        # ).filter(article_count__gt=0)
        # context["popular_articles"] = Article.objects.filter(
        #     is_published=True
        # ).order_by("-view_count")[:5]
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_url_kwarg = "slug"

    # def get_queryset(self):
    #     return Article.objects.filter(is_published=True).select_related(
    #         "author", "category"
    #     )

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        # article.view_count += 1
        # article.save(update_fields=["view_count"])

        # context["related_articles"] = Article.objects.filter(
        #     category=article.category, is_published=True
        # ).exclude(id=article.id)[:4]

        context["related_articles"] = Article.objects.filter(is_published=True).exclude(
            id=article.id
        )[:4]

        # context["categories"] = ArticleCategory.objects.annotate(
        #     article_count=Count("article")
        # ).filter(article_count__gt=0)

        return context


# class CategoryArticleListView(ListView):
#     model = Article
#     template_name = "blog/category_article_list.html"
#     context_object_name = "articles"
#     paginate_by = 10

#     def get_queryset(self):
#         return (
#             Article.objects.filter(
#                 category__slug=self.kwargs["slug"], is_published=True
#             )
#             .select_related("author", "category")
#             .order_by("-published_at")
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["category"] = ArticleCategory.objects.get(slug=self.kwargs["slug"])
#         context["categories"] = ArticleCategory.objects.annotate(
#             article_count=Count("article")
#         ).filter(article_count__gt=0)
#         return context
