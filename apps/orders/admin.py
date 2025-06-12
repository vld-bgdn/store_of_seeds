from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    extra = 0
    readonly_fields = ["price"]
    fields = ["product", "price", "quantity", "cost"]

    def cost(self, instance):
        return instance.cost

    cost.short_description = _("Cost")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_info",
        "created",
        "status",
        "payment_status",
        "total_cost",
        "actions",
    ]
    list_filter = [
        "status",
        "payment_status",
        "created",
        "delivery_method",
        "payment_method",
    ]
    search_fields = [
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "city",
    ]
    inlines = [OrderItemInline]
    readonly_fields = [
        "created",
        "modified",
        "total_cost",
        "ip_address",
        "customer_link",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "status",
                    "payment_status",
                    "payment_method",
                    "delivery_method",
                    "total_cost",
                )
            },
        ),
        (
            _("Customer information"),
            {
                "fields": (
                    "customer_link",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "ip_address",
                )
            },
        ),
        (
            _("Delivery information"),
            {
                "fields": (
                    "address",
                    "postal_code",
                    "city",
                    "country",
                    "cdek_point_id",
                    "cdek_point_address",
                )
            },
        ),
        (
            _("Additional information"),
            {"fields": ("need_consultation", "notes", "created", "modified")},
        ),
    )
    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_completed",
        "mark_as_paid",
    ]

    def customer_info(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.email})"

    customer_info.short_description = _("Customer")

    def customer_link(self, obj):
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return "-"

    customer_link.short_description = _("User account")

    def actions(self, obj):
        return format_html(
            '<a class="button" href="{}">View</a>&nbsp;'
            '<a class="button" href="{}">Invoice</a>',
            reverse("admin:orders_order_change", args=[obj.id]),
            reverse("orders:admin_order_invoice", args=[obj.id]),
        )

    actions.short_description = _("Actions")
    actions.allow_tags = True

    # Custom actions
    def mark_as_processing(self, request, queryset):
        queryset.update(status=Order.Status.PROCESSING)

    mark_as_processing.short_description = _("Mark selected orders as Processing")

    def mark_as_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    mark_as_shipped.short_description = _("Mark selected orders as Shipped")

    def mark_as_completed(self, request, queryset):
        queryset.update(status=Order.Status.COMPLETED)

    mark_as_completed.short_description = _("Mark selected orders as Completed")

    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status=Order.PaymentStatus.PAID)

    mark_as_paid.short_description = _("Mark selected orders as Paid")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            status__in=[Order.Status.NEW, Order.Status.PROCESSING, Order.Status.SHIPPED]
        )
