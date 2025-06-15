from django import forms
from django.utils.translation import gettext_lazy as _


class PromoCodeForm(forms.Form):
    code = forms.CharField(
        label=_("Promo Code"),
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Enter promo code")}
        ),
    )
