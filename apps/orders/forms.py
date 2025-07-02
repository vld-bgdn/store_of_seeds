from django import forms
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
        self.cart = kwargs.pop("cart", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=False)
        if self.cart and self.cart.promo_code:
            order.promo_code = self.cart.promo_code
            order.discount_amount = self.cart.discount_amount
        if commit:
            order.save()
        return order
