from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StripeCustomer
import stripe
from users.models import Teacher


@receiver(post_save, sender=Teacher)
def register_user_on_stripe(sender, instance, created, **kwargs):
    if created:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_customer_obj = stripe.Customer.create(name=instance.get_full_name(), email=instance.email, currency="usd")
        StripeCustomer.objects.create(customer=instance, stripe_customer_id=stripe_customer_obj.id)


