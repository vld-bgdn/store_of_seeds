from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .models import Page


class PageListView(LoginRequiredMixin, ListView):
    """List all pages in admin"""

    model = Page
    template_name = "pages/admin/page_list.html"
    context_object_name = "pages"

    def get_queryset(self):
        return Page.objects.all().order_by("title")


class PageCreateView(LoginRequiredMixin, CreateView):
    """Create new page in admin"""

    model = Page
    template_name = "pages/admin/page_form.html"
    fields = [
        "title",
        "slug",
        "content",
        "is_active",
        "meta_title",
        "meta_description",
        "template_name",
    ]
    success_url = reverse_lazy("pages:page_list")


class PageUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing page in admin"""

    model = Page
    template_name = "pages/admin/page_form.html"
    fields = [
        "title",
        "slug",
        "content",
        "is_active",
        "meta_title",
        "meta_description",
        "template_name",
    ]
    success_url = reverse_lazy("pages:page_list")


class PageDeleteView(LoginRequiredMixin, DeleteView):
    """Delete page in admin"""

    model = Page
    template_name = "pages/admin/page_confirm_delete.html"
    success_url = reverse_lazy("pages:page_list")


class PageDetailView(DetailView):
    """Display page on frontend"""

    model = Page
    template_name_field = "template_name"
    context_object_name = "page"

    def get_queryset(self):
        return Page.objects.filter(is_active=True)
