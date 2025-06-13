from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def pages_menu(request):
    """Context processor that adds pages menu to template context"""
    return {
        "pages_menu_items": [
            {
                "name": _("Pages"),
                "url": reverse("pages:page_list"),
                "icon": "fa-file-alt",
                "children": [
                    {
                        "name": _("All Pages"),
                        "url": reverse("pages:page_list"),
                    },
                    {
                        "name": _("Add New"),
                        "url": reverse("pages:page_create"),
                    },
                ],
            }
        ]
    }
