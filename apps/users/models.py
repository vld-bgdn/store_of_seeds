from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class User(AbstractUser):
    """Custom user model with role-based access control"""

    class Role(models.TextChoices):
        CUSTOMER = "customer", _("Customer")
        MANAGER = "manager", _("Manager")
        CONSULTANT = "consultant", _("Consultant")
        ADMINISTRATOR = "administrator", _("Administrator")

    role = models.CharField(
        _("role"), max_length=20, choices=Role.choices, default=Role.CUSTOMER
    )
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    telegram_chat_id = models.CharField(
        _("telegram chat ID"), max_length=50, blank=True
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name() or self.username


class Profile(TimeStampedModel):
    """Extended user profile"""

    user = models.OneToOneField(
        User, verbose_name=_("user"), related_name="profile", on_delete=models.CASCADE
    )
    avatar = models.ImageField(_("avatar"), upload_to="avatars/", blank=True)
    birth_date = models.DateField(_("birth date"), blank=True, null=True)
    address = models.TextField(_("address"), blank=True)
    email_confirmed = models.BooleanField(_("email confirmed"), default=False)

    class Meta:
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")

    def __str__(self):
        return f"Профиль пользователя {self.user}"
