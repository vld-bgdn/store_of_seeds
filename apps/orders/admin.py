from django.contrib import admin
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created", "total_cost")
    list_filter = ("status", "created", "user")
    search_fields = ("first_name", "last_name", "email", "phone")
    inlines = [OrderItemInline]
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Контактная информация",
            {"fields": ("first_name", "last_name", "email", "phone")},
        ),
        ("Доставка", {"fields": ("address", "postal_code", "city", "country")}),
        (
            "Дополнительно",
            {"fields": ("need_consultation", "notes"), "classes": ("collapse",)},
        ),
    )
