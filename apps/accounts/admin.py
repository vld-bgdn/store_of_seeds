from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, StaffUser, CustomerUser


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Профили"

    def get_fields(self, request, obj=None):
        # Show different fields based on user type
        fields = ["user_type", "avatar", "bio"]

        if obj and hasattr(obj, "userprofile"):
            if obj.userprofile.is_customer:
                fields.extend(["phone", "address"])
            elif obj.userprofile.is_internal_staff:
                fields.extend(["department", "employee_id"])
        else:
            # Show all fields when creating
            fields.extend(["phone", "address", "department", "employee_id"])

        return fields


class StaffUserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Профиль сотрудника"
    fields = ["user_type", "avatar", "bio", "department", "employee_id"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type__in=["staff", "admin"])


class CustomerUserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Профиль покупателя"
    fields = ["user_type", "avatar", "bio", "phone", "address"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type="customer")


class UserAdmin(BaseUserAdmin):
    """Default user admin - shows all users"""

    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_user_type",
        "is_staff",
        "is_active",
    )
    list_filter = BaseUserAdmin.list_filter + ("userprofile__user_type",)

    def get_user_type(self, obj):
        return obj.userprofile.get_user_type_display()

    get_user_type.short_description = "Тип пользователя"


class StaffUserAdmin(admin.ModelAdmin):
    """Staff admin - shows only staff users"""

    inlines = (StaffUserProfileInline,)
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "get_department",
        "get_employee_id",
        "is_active",
    ]
    list_filter = ["is_active", "userprofile__department"]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "userprofile__employee_id",
    ]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "email")}),
        (
            "Права доступа",
            {"fields": ("is_active", "is_staff", "groups", "user_permissions")},
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Exclude superusers (admin accounts)
        return qs.filter(
            userprofile__user_type="staff",
            is_superuser=False,  # This excludes admin accounts
        )

    def get_department(self, obj):
        return obj.userprofile.department if hasattr(obj, "userprofile") else "-"

    get_department.short_description = "Отдел"

    def get_employee_id(self, obj):
        return obj.userprofile.employee_id if hasattr(obj, "userprofile") else "-"

    get_employee_id.short_description = "ID сотрудника"


class CustomerUserAdmin(BaseUserAdmin):
    """Admin for customer users only"""

    inlines = (CustomerUserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_phone",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "date_joined")
    # list_filter = BaseUserAdmin.list_filter + ("userprofile__user_type",)

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "userprofile__phone",
    )

    # Remove staff-related fields from fieldsets
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "email")}),
        ("Разрешения", {"fields": ("is_active",)}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    # def get_user_type(self, obj):
    #     return obj.userprofile.get_user_type_display()

    # get_user_type.short_description = "Тип пользователя"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(userprofile__user_type="customer")

    def get_phone(self, obj):
        return obj.userprofile.phone

    get_phone.short_description = "Телефон"

    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)
    #     # Ensure the user type is set correctly
    #     if hasattr(obj, "userprofile"):
    #         if obj.userprofile.user_type != "customer":
    #             obj.userprofile.user_type = "customer"
    #             obj.userprofile.save()

    # def has_add_permission(self, request):
    #     return True

    # def has_change_permission(self, request, obj=None):
    #     return True

    # def has_delete_permission(self, request, obj=None):
    #     return True


# Register the admin classes
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(StaffUser, StaffUserAdmin)
admin.site.register(CustomerUser, CustomerUserAdmin)
