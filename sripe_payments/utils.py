import stripe
from rest_framework.exceptions import ValidationError
from .models import StripeCustomer, Subscription
from datetime import timedelta
from datetime import datetime
from django.conf import settings

STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

def create_stripe_customer(name,email):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.Customer.create(name=name, email=email)


def save_stripe_customer_obj_locally(local_user,stripe_customer_obj): 
   return StripeCustomer.objects.create(customer=local_user, stripe_customer_id=stripe_customer_obj.id)


def get_stripe_customer_id(local_user):
    stripe_customer_obj = StripeCustomer.objects.filter(customer=local_user).first()
    if not stripe_customer_obj:
        stripe_customer_obj = create_stripe_customer(local_user.get_full_name(),local_user.email)
        save_stripe_customer_obj_locally(local_user, stripe_customer_obj)
        return stripe_customer_obj.id
    else:
        return stripe_customer_obj.stripe_customer_id


def get_data_from_stripe_subscription_object(stripe_subscription_obj):
    """
    to get relevant data from stripe subscription object to pass it to Subscription Serializer
    """
    data = {}
    data['stripe_subscription_id'] = stripe_subscription_obj.id
    data['subscription_status'] = stripe_subscription_obj.status
    return data


def get_customer_id_from_stripe_customer_id(stripe_customer_id):
    return StripeCustomer.objects.filter(stripe_customer_id=stripe_customer_id).first().customer.pk


def attach_payment_method_to_customer(stripe_customer_id, stripe_pm_id):
    stripe.api_key = STRIPE_SECRET_KEY
    try:
        return stripe.PaymentMethod.attach(stripe_pm_id ,customer=stripe_customer_id)
    except stripe.error.StripeError as stripe_error:
        raise ValidationError(str(stripe_error))


def get_all_products():
    stripe.api_key = STRIPE_SECRET_KEY
    products = stripe.Product.list()
    return products


def get_premium_subscription():
    stripe.api_key = STRIPE_SECRET_KEY
    product = stripe.Product.retrieve("prod_LsJ7mdsVVkbzFh")
    price = stripe.Price.retrieve(product.default_price)
    data = {
        'id':product.id,
        'name':product.name,
        'default_amount':price.unit_amount/100,
        'currency':price.currency,
    }
    return data


def get_subscription_detail(stripe_subscription_id):
    stripe.api_key = STRIPE_SECRET_KEY
    subscription = stripe.Subscription.retrieve(stripe_subscription_id)
    subscription_representation = {}
    subscription_representation['id'] = subscription.id
    subscription_representation['status'] = subscription.status
    subscription_representation['price'] = subscription.plan.amount / 100
    subscription_representation['expiry_date'] = datetime.fromtimestamp(subscription.current_period_end).strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    renewal_date = datetime.fromtimestamp(subscription.current_period_end) + timedelta(days=1)
    subscription_representation['renewal_date'] =  renewal_date.strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])
    return subscription_representation


def get_subscription_id_for_customer(local_customer_id):
    if Subscription.objects.filter(customer=local_customer_id).first():
        return Subscription.objects.filter(customer=local_customer_id).first().stripe_subscription_id
    return None

def get_fake_payment_method_id(card_number= "4242424242424242",expiry_month=12,expiry_year=2023,cvc=314):
    stripe.api_key = STRIPE_SECRET_KEY
    payment_method = stripe.PaymentMethod.create(
    type="card",
    card={
        "number": card_number,
        "exp_month": expiry_month,
        "exp_year": expiry_year,
        "cvc": cvc,
    },
    )
    return payment_method.id


def cancel_subscription(subscription_id):
    stripe.api_key = STRIPE_SECRET_KEY
    stripe.Subscription.modify(subscription_id,metadata={"cancel_at_period_end":True})


def save_customer_card(stripe_customer_id, source):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.Customer.create_source(stripe_customer_id,source=source)


def get_customer_from_stripe(stripe_customer_id):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.Customer.retrieve(stripe_customer_id)


def attach_payment_method_to_user(stripe_customer_id, payment_method_token):
    stripe.api_key = STRIPE_SECRET_KEY
    try:
        output =stripe.PaymentMethod.attach(payment_method_token,customer=stripe_customer_id,)
        updation_fields = {
            "default_payment_method":payment_method_token
        }
        update_stripe_customer_invoice_settings(stripe_customer_id, updation_fields)
    except stripe.error.InvalidRequestError as e:
        raise ValidationError(e.user_message)
    except Exception:
        raise ValidationError("Not able to attach payment method to user")


def get_all_cards_of_user(stripe_customer_id):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.Customer.list_sources(stripe_customer_id,object="card")


def get_all_payment_methods_of_user(stripe_customer_id):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.Customer.list_payment_methods(stripe_customer_id,type="card",)


def delete_card_of_user(stripe_customer_id,card_id):
    stripe.api_key = STRIPE_SECRET_KEY
    stripe.Customer.delete_source(stripe_customer_id,card_id)


def deatach_payment_method_of_user(payment_method_id):
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe.PaymentMethod.detach(payment_method_id)


def number_of_saved_stripe_payment_methods(local_user):
    stripe_user = StripeCustomer.objects.filter(customer=local_user).first()
    if stripe_user:
        result = get_all_payment_methods_of_user(stripe_user.stripe_customer_id)
        return len(result.data)
    return 0


def update_stripe_customer_invoice_settings(stripe_customer_id, updation_fields):
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        return stripe.Customer.modify(stripe_customer_id, invoice_settings=updation_fields,)
    except stripe.error.InvalidRequestError as e:
        raise ValidationError(e.user_message)