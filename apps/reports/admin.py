from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Report

admin.site.site_header = "Админка"
admin.site.site_title = "Админка магазина микрозелени"
admin.site.index_title = "Добро пожаловать в Админку магазина микрозелени"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "start_date", "end_date", "is_ready"]
    list_filter = ["report_type", "is_ready"]
    search_fields = ["name"]
    readonly_fields = ["created", "modified"]
    actions = ["generate_reports"]  # This should be a list of strings

    def generate_reports(self, request, queryset):
        for report in queryset:
            report.is_ready = True
            report.generated_by = request.user
            report.save()
        self.message_user(
            request, _("Selected reports have been queued for generation")
        )

    generate_reports.short_description = _("Generate selected reports")
