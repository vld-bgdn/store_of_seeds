from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_ckeditor_5 import urls as ckeditor5_urls

urlpatterns = [
    path(
        "admin/",
        include(
            [
                path("", admin.site.urls),
                path("reports/", include("apps.reports.urls", namespace="reports")),
                path("pages/", include("apps.pages.urls", namespace="pages")),
            ]
        ),
    ),
    path("cart/", include("apps.cart.urls", namespace="cart")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("", include("apps.products.urls", namespace="products")),
    path("admin/reports/", include("apps.reports.urls", namespace="reports")),
    path("admin/pages/", include("apps.pages.urls", namespace="pages")),
    # path(
    #     "ckeditor5/image_upload/",
    #     custom_upload_file,
    #     name="ckeditor5_custom_upload_file",
    # ),
    path("ckeditor5/", include(ckeditor5_urls)),
    path("pages/", include("apps.pages.urls", namespace="pages_frontend")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
