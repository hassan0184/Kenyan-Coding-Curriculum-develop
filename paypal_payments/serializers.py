from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
import braintree
from users.utils import get_user_subscription_type
from rest_framework.exceptions import ValidationError, NotFound
from .models import PaypalSubscription
from .utils import (
    create_subscription_for_user, get_paypal_customer_id_from_local_customer,
    save_payment_method, create_customer, get_subscription_id_for_customer, 
    get_all_payment_methods, cancel_subscription, create_subscription,
    save_subscription_locally,get_subscription, update_subscrption)

    
class PaypalPlanSerializers(ModelSerializer):
    class Meta:
        model = braintree.Plan
        fields = '__all__'

class CreatePaypalSubscriptionSerializer(serializers.Serializer):
    payment_method_nounce = serializers.CharField()
    plan_id = serializers.CharField()


class SavePaymentMethodSerializer(serializers.Serializer):
    payment_method_nounce = serializers.CharField()
    
    def validate(self, attrs):
        local_user = self.context.get("request").user
        gateway = get_user_subscription_type(local_user)[1]
        if gateway == "Stripe":
            raise ValidationError("You cannot save card, your default payment method is Stripe.")
        return attrs


    def save(self, **kwargs):
        local_user = self.context.get("request").user
        paypal_customer_id = get_paypal_customer_id_from_local_customer(local_user)
        if paypal_customer_id is None:
            create_customer(local_user.first_name, local_user.last_name, local_user.email, local_user)
        paypal_customer_id = get_paypal_customer_id_from_local_customer(local_user)
        payment_method_token = self.validated_data.get('payment_method_nounce')
        save_payment_method(paypal_customer_id,payment_method_token)


class PaymentMethodSerializer(serializers.Serializer):
    email = serializers.CharField()


class CancelPaypalSubscriptionSerializer(serializers.Serializer):
    subscription_id = serializers.CharField()

    def save(self, **kwargs):
        subscription_id = self.validated_data.get("subscription_id")
        subscription = get_subscription(subscription_id)
        update_subscrption(subscription_id, 
        number_of_billing_cycles=subscription.current_billing_cycle)


    

class UpgradeSubscriptionSerializer(serializers.Serializer):
    paypal_plan_id = serializers.CharField()

    def validate_paypal_plan_id(self, paypal_plan_id):
        return paypal_plan_id

    def save(self, **kwargs):
        plan_id = self.validated_data.get("paypal_plan_id")
        local_user = self.context.get("request").user
        paypal_customer_id = get_paypal_customer_id_from_local_customer(local_user)
        if paypal_customer_id is None:
            raise NotFound("no paypal customer found")
        payment_methods = get_all_payment_methods(paypal_customer_id) 
        if not get_all_payment_methods(paypal_customer_id):
            raise NotFound("no defualt paypal account is stored")
        result = create_subscription(plan_id, payment_methods[0].token)
        save_subscription_locally(local_user, result.subscription.id, result.subscription.status,)        
        










