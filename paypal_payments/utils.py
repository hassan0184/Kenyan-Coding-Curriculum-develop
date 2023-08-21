import braintree
from django.conf import settings
from .models import PaypalCustomer, PaypalSubscription
from django.apps import apps
from rest_framework.exceptions import ValidationError, NotFound


try:
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id=settings.MERCHANT_ID,
            public_key=settings.PUBLIC_ID,
            private_key=settings.PRIVATE_ID
        )
    )
except Exception as e:
    print(e)


def save_paypal_customer_id_locally(paypal_customer_id, local_customer):
    # app_name ,DbClass = settings.PAYPAL_CUSTOMER.split(".")
    # DbModel = apps.get_model(app_name, DbClass)
    paypal_obj = PaypalCustomer.objects.filter(paypal_customer_id=paypal_customer_id).first()
    if not paypal_obj:
        PaypalCustomer.objects.create(paypal_customer_id=paypal_customer_id, local_customer=local_customer)



def create_customer(first_name,last_name,email,local_customer):
    if not PaypalCustomer.objects.filter(local_customer=local_customer).first():
        result = gateway.customer.create({
            "first_name": first_name,
            "last_name": last_name,
            "email":email,
        })
        if result.is_success:
            save_paypal_customer_id_locally(result.customer.id, local_customer)
        return result
    return False


def get_customer_from_local_customer_id(local_customer_id):
    paypal_customer_id = PaypalCustomer.objects.get_paypal_customer_id(local_customer_id)
    return paypal_customer_id


def create_plan(plan_name,billing_frequency,currency_iso_code,price,**kwargs):
    plan = {
        "name": plan_name,
        "billing_frequency": billing_frequency,# in months
        "currency_iso_code": currency_iso_code,
        "price": price                         # in dollars
    }
    for key,value in kwargs.items():
        plan[key] = value
    result = gateway.plan.create(plan)
    return result


def create_subscription(plan_id, payment_method_token):
    result = gateway.subscription.create({
        "payment_method_token": payment_method_token,
        "plan_id": plan_id
    })
    if not result.is_success:
        raise ValidationError(result.message)
    return result


def create_payment_method_token(paypal_customer_id, nonce_from_the_client):
    result = gateway.payment_method.create({
        "customer_id": paypal_customer_id,
        "payment_method_nonce": nonce_from_the_client
    })
    if not result.is_success:
        raise ValidationError(result.message)
    return result


def create_subscription_for_user(local_customer_id, plan_id, nonce_from_the_client):
    paypal_customer_id = get_customer_from_local_customer_id(local_customer_id)
    result = create_payment_method_token(paypal_customer_id,nonce_from_the_client)
    if result.is_success:
        result = create_subscription(plan_id, result.payment_method.token)
        save_subscription_locally(PaypalCustomer.objects.get(local_customer=local_customer_id).local_customer,result.subscription.id,result.subscription.status,)
        return result
    raise ValidationError(result.message)


def get_client_token(local_customer_id):
    paypal_customer_id =  get_customer_from_local_customer_id(local_customer_id)
    # pass client_token to your front-end
    client_token = gateway.client_token.generate({
        "customer_id": paypal_customer_id
    })
    return client_token


def get_all_plans_from_paypal():
    return gateway.plan.all()


def get_all_plans():
    plan_representation = {
            "id" :"id",
            "name": "plan_name",
            "price": "price"                         # in dollars
        }
    plans = []
    for plan in get_all_plans_from_paypal():
        plan_representation['id'] = plan.id
        plan_representation['name'] = plan.name
        plan_representation['price'] = f"{plan.price} {plan.currency_iso_code}"
        plans.append(plan_representation)
    return plans



def save_subscription_locally(local_customer, subscription_id, subscription_status):
    return PaypalSubscription.objects.create(local_customer=local_customer, paypal_subscription_id=subscription_id, subscription_status=subscription_status)


def update_subscription_status(local_customer, subscription_status):
    paypal_subscription_obj = PaypalSubscription.objects.filter(local_customer=local_customer).first()
    if paypal_subscription_obj:
        paypal_subscription_obj.subscription_status = subscription_status
        paypal_subscription_obj.save()
        return True
    return False



def get_all_subscription_for_a_plan(plan_id):
    collection = gateway.subscription.search(
        braintree.SubscriptionSearch.plan_id == plan_id
    )
    subscriptions = []
    for subscription in collection:
        subscriptions.append(serializer_subscription(subscription))
    return subscriptions


def serializer_subscription(subscription):
    subscription_representation = {
            "id" :"id",
            "plan_id": "plan_id",
            "price": "price"                         # in dollars
    }
    subscription_representation['id'] = subscription.id
    subscription_representation['plan_id'] = subscription.plan_id
    subscription_representation['price'] = subscription.price
    return subscription_representation

    
def get_subscription_detail(paypal_subscription_id):
    subscription = gateway.subscription.find(paypal_subscription_id)
    subscription_representation = {}
    subscription_representation['id'] = subscription.id
    subscription_representation['status'] = subscription.status
    subscription_representation['price'] = subscription.price
    subscription_representation['expiry_date'] = subscription.billing_period_end_date
    subscription_representation['renewal_date'] = subscription.next_billing_date
    return subscription_representation


def get_subscription_id_for_customer(local_customer):
    paypal_subscription_obj = PaypalSubscription.objects.filter(local_customer=local_customer).first() 
    if paypal_subscription_obj:
        return paypal_subscription_obj.paypal_subscription_id
    raise NotFound("no paypal subscription found against user")


def cancel_subscription(paypal_subscription_id):
    try:
        result = gateway.subscription.cancel(paypal_subscription_id)
    except Exception:
        raise NotFound("no subscription found")


def get_paypal_customer_id_from_local_customer(local_customer):
    paypal_customer = PaypalCustomer.objects.filter(local_customer=local_customer).first() 
    if paypal_customer:
        return paypal_customer.paypal_customer_id


def save_payment_method(paypal_customer_id, payment_method_nounce):
    result = gateway.payment_method.create({
    "customer_id": paypal_customer_id,
    "payment_method_nonce": payment_method_nounce})
    if result.is_success:
        return result.payment_method.token
    else:
        raise ValidationError(result.message)


def get_all_payment_methods(paypal_customer_id):
    try:
        customer = gateway.customer.find(paypal_customer_id)
    except Exception as e:
        raise NotFound("no user found on paypal")
    return customer.payment_methods
    

def number_of_saved_paypal_payment_methods(local_user):
    paypal_customer =  PaypalCustomer.objects.filter(local_customer=local_user).first()
    if paypal_customer:
        return len(get_all_payment_methods(paypal_customer.paypal_customer_id))

def get_subscription(subscription_id):
    try:
        result = gateway.subscription.find(subscription_id)
    except NotFound:
        raise NotFound(f'no subscription with id {subscription_id} was found')
    return result

def update_subscrption(subscription_id, **kwargs):
    try:
        result = gateway.subscription.update(subscription_id,kwargs)
    except NotFound:
        raise NotFound(f'no subscription with id {subscription_id} was found')
    if not result.is_success:
        raise ValidationError(result.message)
    return result