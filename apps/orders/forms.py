from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "delivery_method",
            "address",
            "postal_code",
            "city",
            "country",
            "payment_method",
            "notes",
            "need_consultation",
        ]
        widgets = {
            "delivery_method": forms.RadioSelect(),
            "payment_method": forms.RadioSelect(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields["phone"].required = True
