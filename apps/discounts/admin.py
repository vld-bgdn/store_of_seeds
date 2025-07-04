from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PromoCode, PromoCodeUse


class PromoCodeUseInline(admin.TabularInline):
    model = PromoCodeUse
    extra = 0
    readonly_fields = ["created", "order", "discount_amount", "user"]
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
        "current_uses",
    ]
    list_filter = ["discount_type", "active"]
    search_fields = ["code"]
    readonly_fields = ["current_uses"]
    inlines = [PromoCodeUseInline]
    actions = ["mark_as_active", "mark_as_inactive"]

    def mark_as_active(self, request, queryset):
        queryset.update(active=True)

    mark_as_active.short_description = _("Mark selected promo codes as active")

    def mark_as_inactive(self, request, queryset):
        queryset.update(active=False)

    mark_as_inactive.short_description = _("Mark selected promo codes as inactive")


@admin.register(PromoCodeUse)
class PromoCodeUseAdmin(admin.ModelAdmin):
    list_display = [
        "promo_code",
        "order",
        "discount_amount",
        "created",
        "user",
    ]
    list_filter = ["promo_code"]
    search_fields = ["promo_code__code", "user__email", "order__id"]
    readonly_fields = ["created", "modified"]
