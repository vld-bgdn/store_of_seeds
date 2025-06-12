from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PromoCode, PromoCodeUse


class PromoCodeUseInline(admin.TabularInline):
    model = PromoCodeUse
    extra = 0
    readonly_fields = ["created", "user", "order", "discount_amount"]
    can_delete = False


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_type",
        "discount_value",
        "valid_from",
        "valid_to",
        "active",
        "usage_count",
    ]
    list_filter = ["discount_type", "active"]
    search_fields = ["code"]
    readonly_fields = ["usage_count"]
    inlines = [PromoCodeUseInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "code",
                    "active",
                    "discount_type",
                    "discount_value",
                    "max_discount",
                    "min_order_amount",
                )
            },
        ),
        (
            _("Validity"),
            {"fields": ("valid_from", "valid_to", "max_uses", "current_uses")},
        ),
        (_("Restrictions"), {"fields": ("for_all_users", "for_first_order", "users")}),
    )
    filter_horizontal = ["users"]

    def usage_count(self, obj):
        return obj.uses.count()

    usage_count.short_description = _("Usage count")


@admin.register(PromoCodeUse)
class PromoCodeUseAdmin(admin.ModelAdmin):
    list_display = ["promo_code", "user", "order", "discount_amount", "created"]
    list_filter = ["promo_code"]
    search_fields = ["promo_code__code", "user__email", "order__id"]
    readonly_fields = ["created", "modified"]
