from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="article_list"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    # path(
    #     "category/<slug:slug>/",
    #     views.CategoryArticleListView.as_view(),
    #     name="category_article_list",
    # ),
]
