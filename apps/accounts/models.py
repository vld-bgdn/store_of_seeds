from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    USER_TYPES = [
        ("customer", "Покупатель"),
        ("staff", "Персонал"),
        ("admin", "Админ"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        _("Тип пользователя"),
        max_length=20,
        choices=USER_TYPES,
        default="customer",
    )
    avatar = models.ImageField(_("Аватар"), upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(_("О себе"), max_length=500, blank=True)

    # Customer-specific fields
    phone = models.CharField(_("Номер телефона"), max_length=20, blank=True)
    address = models.TextField(_("Адрес"), blank=True)

    # Staff-specific fields
    department = models.CharField(_("Отдел"), max_length=100, blank=True)
    employee_id = models.CharField(_("Идентификатор"), max_length=20, blank=True)

    def get_user_orders(self):
        """Get all orders for this user"""
        return self.user.order_set.all().order_by("-created_at")

    @property
    def is_customer(self):
        return self.user_type == "customer"

    @property
    def is_internal_staff(self):
        return self.user_type in ["staff", "admin"]

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class StaffUser(User):
    """Proxy model for staff users"""

    class Meta:
        proxy = True
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class CustomerUser(User):
    """Proxy model for customer users"""

    class Meta:
        proxy = True
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
