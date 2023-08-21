from django.db import models
from django.conf import settings
from rest_framework.exceptions import NotFound
from .choices import SubscriptionStatus
# Create your models here.

class PaypalCustomerManager(models.Manager):
    def get_paypal_customer_id(self,local_customer_id):
        paypal_customer = self.filter(local_customer=local_customer_id).first()
        if not paypal_customer:
            raise NotFound(f"no customer found on paypal with local id {local_customer_id}")
        return paypal_customer.paypal_customer_id


class PaypalCustomer(models.Model):
    local_customer = models.ForeignKey(to=settings.PAYPAL_CUSTOMER,on_delete=models.CASCADE)
    paypal_customer_id = models.CharField(max_length=250)
    
    objects = PaypalCustomerManager()


class PaypalSubscription(models.Model):
    local_customer = models.ForeignKey(to=settings.PAYPAL_CUSTOMER,on_delete=models.CASCADE)
    paypal_subscription_id = models.CharField(max_length=255)
    subscription_status = models.CharField(max_length=100, null=True, choices=SubscriptionStatus.choices)


