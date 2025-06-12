from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.CategoryListView.as_view(), name="category_list"),
    path(
        "category/<slug:category_slug>/",
        views.ProductListView.as_view(),
        name="product_list_by_category",
    ),
    path(
        "product/<slug:product_slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("search/", views.ProductListView.as_view(), name="product_search"),
]
