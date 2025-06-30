from django.views.generic import DetailView
from .models import Page


class PageDetailView(DetailView):
    """Display page on frontend"""

    model = Page
    template_name_field = "template_name"
    context_object_name = "page"

    def get_queryset(self):
        return Page.objects.filter(is_active=True)
