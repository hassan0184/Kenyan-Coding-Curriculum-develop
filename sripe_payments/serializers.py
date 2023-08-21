from django.forms import CharField
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.conf import settings
from .models import Subscription, StripeCustomer
from users.utils import get_user_subscription_type
from .utils import (
    attach_payment_method_to_customer,
    get_stripe_customer_id,
    get_subscription_id_for_customer,
    save_customer_card,
    attach_payment_method_to_user,
    create_stripe_customer,
    get_subscription_id_for_customer,
    cancel_subscription
)
import stripe


STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class StripeSubscriptionSerializer(serializers.Serializer):
    stripe_product_id = serializers.CharField()
    stripe_payment_method_id = serializers.CharField()


    def save(self, **kwargs):
        try:
            local_user = self.context.get("user")
            stripe.api_key = STRIPE_SECRET_KEY
            stripe_customer_id = get_stripe_customer_id(local_user)
            stripe_product_obj = stripe.Product.retrieve(self.validated_data.get("stripe_product_id"))
            stripe_payment_method_id = self.validated_data.get("stripe_payment_method_id")
            attach_payment_method_to_customer(stripe_customer_id, stripe_payment_method_id)
            stripe.Customer.modify(stripe_customer_id, invoice_settings={"default_payment_method":stripe_payment_method_id})
            stripe_subscription_obj = stripe.Subscription.create(
                customer=stripe_customer_id,
                items = [{"price":stripe_product_obj.default_price},]
            )
            Subscription.objects.create(customer=local_user,stripe_subscription_id=stripe_subscription_obj.id,subscription_status=stripe_subscription_obj.status)
            return stripe_subscription_obj
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)
        except Exception as e:
            raise ValidationError(e)



class CancelStripeSubscriptionSerializer(serializers.Serializer):
    def save(self, **kwargs):
        local_user = self.context.get("request").user
        subscription_id = get_subscription_id_for_customer(local_user) 
        if subscription_id:
            cancel_subscription(subscription_id)
        else:
            raise ValidationError("User has got no subscription to cancel")


class UpdateSubscriptionSerializer(serializers.Serializer):
    stripe_product_id =  serializers.CharField()
    
    def save(self,**kwargs):
        try:
            stripe.api_key = STRIPE_SECRET_KEY
            local_user = self.context.get("request").user
            stripe_product_obj = stripe.Product.retrieve(self.validated_data.get("stripe_product_id"))
            stripe_customer_id = get_stripe_customer_id(local_user)
            stripe_subscription_obj = stripe.Subscription.create(
                customer=stripe_customer_id,
                items = [{"price":stripe_product_obj.default_price},]
            )
            Subscription.objects.create(customer=local_user,stripe_subscription_id=stripe_subscription_obj.id,subscription_status=stripe_subscription_obj.status)
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)
        except Exception as e:
            raise ValidationError(e)


class SaveCardSerializer(serializers.Serializer):
    payment_method_token = serializers.CharField()

    def validate(self, attrs):
        local_user = self.context.get("request").user
        gateway = get_user_subscription_type(local_user)[1]
        if gateway == "Paypal":
            raise ValidationError("You cannot save card, your default payment method is Paypal.")
        return attrs
            
    def save(self, **kwargs):
        try:
            payment_method_token = self.validated_data.get('payment_method_token')
            local_user = self.context.get("request").user
            stripe_customer_id = get_stripe_customer_id(local_user)
            attach_payment_method_to_user(stripe_customer_id,payment_method_token)
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(e.user_message)
        except Exception as e:
            raise ValidationError(e)



class CardSerializer(serializers.Serializer):
    id = serializers.CharField()
    brand = serializers.CharField(source = "card.brand")
    last4 = serializers.CharField(source = "card.last4")
    exp_month = serializers.CharField(source= "card.exp_month")
    exp_year = serializers.CharField(source = "card.exp_year")


