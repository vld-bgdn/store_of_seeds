from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "pages"

urlpatterns = [
    # Admin URLs
    path("admin/list/", views.PageListView.as_view(), name="page_list"),
    path("admin/create/", views.PageCreateView.as_view(), name="page_create"),
    path("admin/edit/<int:pk>/", views.PageUpdateView.as_view(), name="page_edit"),
    path("admin/delete/<int:pk>/", views.PageDeleteView.as_view(), name="page_delete"),
    # Frontend URLs
    path("<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
]
