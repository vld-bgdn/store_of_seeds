from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from apps.orders.models import Order
from apps.products.models import Product


class ReportListView(LoginRequiredMixin, ListView):
    """List all available reports"""

    template_name = "reports/report_list.html"
    context_object_name = "reports"

    def get_queryset(self):
        # In a real app, this would return actual Report objects
        return []


class ReportDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific report"""

    template_name = "reports/report_detail.html"
    context_object_name = "report"

    def get_object(self, queryset=None):
        # Mock report object
        return {
            "id": self.kwargs["pk"],
            "name": f"Report {self.kwargs['pk']}",
            "type": "Sales",
            "period": "2023-01-01 to 2023-12-31",
        }


class QuickSalesReportView(LoginRequiredMixin, TemplateView):
    """Quick sales report for last N days"""

    template_name = "reports/quick_sales.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self.kwargs["days"]
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        orders = Order.objects.filter(
            created__range=(start_date, end_date),
            status__in=["completed", "shipped", "delivered"],
        )

        total_sales = orders.aggregate(total=Sum("total_cost"))["total"] or 0
        order_count = orders.count()

        context.update(
            {
                "days": days,
                "start_date": start_date,
                "end_date": end_date,
                "total_sales": total_sales,
                "order_count": order_count,
                "orders": orders[:10],  # Show last 10 orders
            }
        )
        return context


class InventoryReportView(LoginRequiredMixin, TemplateView):
    """Current inventory status report"""

    template_name = "reports/inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.annotate(
            total_ordered=Sum("order_items__quantity")
        ).order_by("-stock")

        low_stock = products.filter(stock__lt=10)
        out_of_stock = products.filter(stock=0)

        context.update(
            {
                "products": products,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock,
                "total_products": products.count(),
            }
        )
        return context


class GenerateSalesReportView(LoginRequiredMixin, TemplateView):
    """Generate sales report"""

    template_name = "reports/generate_sales.html"

    def get(self, request, *args, **kwargs):
        # In a real app, this would generate a PDF/Excel report
        return JsonResponse(
            {"status": "success", "message": "Sales report generation started"}
        )


class GenerateProductReportView(LoginRequiredMixin, TemplateView):
    """Generate product performance report"""

    template_name = "reports/generate_product.html"

    def get(self, request, *args, **kwargs):
        # In a real app, this would generate a PDF/Excel report
        return JsonResponse(
            {"status": "success", "message": "Product report generation started"}
        )
