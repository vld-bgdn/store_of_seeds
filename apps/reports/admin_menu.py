from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def reports_menu(request):
    """Context processor that adds reports menu to template context"""
    return {
        "reports_menu_items": [
            {
                "name": _("Reports"),
                "url": reverse("reports:report_list"),
                "icon": "fa-chart-bar",
                "children": [
                    {
                        "name": _("Sales Reports"),
                        "url": reverse(
                            "reports:quick_sales_report", kwargs={"days": 7}
                        ),
                    },
                    {
                        "name": _("Inventory"),
                        "url": reverse("reports:quick_inventory_report"),
                    },
                ],
            }
        ]
    }
