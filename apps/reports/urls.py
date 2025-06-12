from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "reports"

urlpatterns = [
    path("", login_required(views.ReportListView.as_view()), name="report_list"),
    path(
        "<int:pk>/",
        login_required(views.ReportDetailView.as_view()),
        name="report_detail",
    ),
    # Quick reports
    path(
        "sales/<int:days>/",
        login_required(views.QuickSalesReportView.as_view()),
        name="quick_sales_report",
    ),
    path(
        "inventory/",
        login_required(views.InventoryReportView.as_view()),
        name="quick_inventory_report",
    ),
    # Report generation
    path(
        "generate/sales/",
        login_required(views.GenerateSalesReportView.as_view()),
        name="generate_sales_report",
    ),
    path(
        "generate/products/",
        login_required(views.GenerateProductReportView.as_view()),
        name="generate_product_report",
    ),
]
