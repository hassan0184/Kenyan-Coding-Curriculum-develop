from django.db import models
from common_utilities.utils import get_object_or_not_found_exception

# Create your models here.

class StripeCustomerManage(models.Manager):
    def get_customer_from_stripe_id(self,stripe_id):
        return self.filter(stripe_customer_id=stripe_id)



class StripeCustomer(models.Model):
    customer = models.OneToOneField(to="users.Teacher", on_delete=models.CASCADE, related_name="stripe_customer")
    stripe_customer_id = models.CharField(max_length=255, null=True)

    objects = StripeCustomerManage()


class Subscription(models.Model):
    customer = models.ForeignKey(to="users.Teacher", on_delete=models.CASCADE, related_name="subscription_plans")
    stripe_subscription_id = models.CharField(max_length=255)
    subscription_status = models.CharField(max_length=100, null=True)


class Charge(models.Model):
    customer = models.ForeignKey(to="users.Teacher", on_delete=models.CASCADE, related_name="charges")
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_time = models.DateTimeField(auto_now_add=True)