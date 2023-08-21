from django.contrib import admin
from .models import Subscription, StripeCustomer
# Register your models here.


admin.site.register(Subscription)
admin.site.register(StripeCustomer)