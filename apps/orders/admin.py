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
    fields = ["product", "price", "quantity"]

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
        "order_actions",  # Changed from "actions" to "order_actions"
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
        "customer_link",
    ]
    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_completed",
        "mark_as_paid",
    ]

    def customer_info(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.email})"

    customer_info.short_description = _("Покупатель")

    # def customer_link(self, obj):
    #     if obj.user:
    #         url = reverse("admin:users_user_change", args=[obj.user.id])
    #         return format_html('<a href="{}">{}</a>', url, obj.user)
    #     return "-"

    def customer_link(self, obj):
        if obj.user:
            url = reverse(
                "admin:auth_user_change", args=[obj.user.id]
            )  # Changed from users_user_change
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return "-"

    customer_link.short_description = _("Пользователь")

    def order_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Просмотр</a>&nbsp;',
            # '<a class="button" href="{}">Invoice</a>',
            reverse("admin:orders_order_change", args=[obj.id]),
            # reverse("orders:admin_order_invoice", args=[obj.id]),
        )

    order_actions.short_description = _("Действия")
    # order_actions.allow_tags = (
    #     True  # Note: allow_tags is deprecated in newer Django versions
    # )

    # Custom actions
    def mark_as_processing(self, request, queryset):
        queryset.update(status=Order.Status.PROCESSING)

    mark_as_processing.short_description = _("Пометить заказы как В работе")

    def mark_as_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    mark_as_shipped.short_description = _("Пометить заказы как Отправленные")

    def mark_as_completed(self, request, queryset):
        queryset.update(status=Order.Status.COMPLETED)

    mark_as_completed.short_description = _("Пометить заказы как Завершенные")

    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status=Order.PaymentStatus.PAID)

    mark_as_paid.short_description = _("Пометить заказа как Оплаченные")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            status__in=[Order.Status.NEW, Order.Status.PROCESSING, Order.Status.SHIPPED]
        )
