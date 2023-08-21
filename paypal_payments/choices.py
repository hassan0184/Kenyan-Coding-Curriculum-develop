from django.db import models
from django.utils.translation import gettext_lazy as _


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "Active", _('Active')
    CANCELED = "Canceled", _('Canceled')
    EXPIRED = "Expired", _("Expired")
    PAST_DUE = "PastDue", _('Past Due')
    PENDING = "Pending", _('Pending')