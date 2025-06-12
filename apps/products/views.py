from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Category, Product


class ProductListView(ListView):
    """View for displaying product list"""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)

        # Filter by category
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            subcategories = category.children.all()
            if subcategories.exists():
                # Include products from subcategories
                queryset = queryset.filter(
                    Q(category=category) | Q(category__in=subcategories)
                )
            else:
                queryset = queryset.filter(category=category)

        # Filter by search query
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(short_description__icontains=search_query)
                | Q(full_description__icontains=search_query)
            )

        # Filter by difficulty level
        difficulty = self.request.GET.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        # Filter by price range
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset.select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(parent__isnull=True)

        # Add current category to context
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            context["current_category"] = get_object_or_404(
                Category, slug=category_slug
            )

        return context


class ProductDetailView(DetailView):
    """View for displaying product details"""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "product_slug"

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add related products
        product = self.object
        related_products = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id)[:4]

        context["related_products"] = related_products
        return context


class CategoryListView(ListView):
    """View for displaying category list"""

    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True)
