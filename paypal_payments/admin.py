from django.contrib import admin
from .models import PaypalCustomer, PaypalSubscription
# Register your models here.
admin.site.register(PaypalCustomer)
admin.site.register(PaypalSubscription)