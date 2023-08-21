import stripe
from django.shortcuts import render, HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView
from users.permissions import IsTeacher
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .models import StripeCustomer, Subscription
from django.conf import settings
from .serializers import (
    SubscriptionSerializer,
    StripeSubscriptionSerializer,
    SaveCardSerializer,
    CardSerializer,
    CancelStripeSubscriptionSerializer,
    UpdateSubscriptionSerializer,
)
from .utils import (
    get_data_from_stripe_subscription_object,
    get_customer_id_from_stripe_customer_id,
    get_all_products,
    get_premium_subscription,
    get_fake_payment_method_id,
    get_all_cards_of_user,
    get_stripe_customer_id,
    delete_card_of_user,
    get_all_payment_methods_of_user,
    deatach_payment_method_of_user,
    get_subscription_detail,
    )
# Create your views here.

class CreateSubscriptionView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = StripeSubscriptionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class CancelSubscriptionView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CancelStripeSubscriptionSerializer


class UpdateSubscriptionView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = UpdateSubscriptionSerializer



@csrf_exempt
def subscription_update_webhook(request, *args, **kwargs):
    endpoint_secret = """whsec_AXgpUySHmZbNhxXekKcW2Hqm1v6Ou8bT"""
    event = None
    payload = request.body
    sig_header = request.headers['STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'customer.subscription.updated':
        stripe_subscription_obj = event['data']['object']
        local_subscription = Subscription.objects.filter(stripe_subscription_id=stripe_subscription_obj.id).first()
        data = get_data_from_stripe_subscription_object(stripe_subscription_obj)
        data['customer'] = get_customer_id_from_stripe_customer_id(stripe_subscription_obj.customer)
        subscription_serializer =SubscriptionSerializer(instance=local_subscription, data=data)
        subscription_serializer.is_valid(raise_exception=True)
        subscription_serializer.save()

    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)


class GetStripePublicKeyView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self,request,*args, **kwargs):
        return Response({'public key':settings.STRIPE_PUBLISHABLE_KEY})


class GetAllStripeProductsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self,request,*args, **kwargs):
        return Response({'products':[get_premium_subscription()]})


class GetFakePaymentMethodId(APIView):
    def get(self,request,*args, **kwargs):
        return Response({'payment_method_id':get_fake_payment_method_id()})


class SaveCardView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = SaveCardSerializer


class GetAllCardsOfUserView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CardSerializer
    
    def get_queryset(self):
        stripe_customer_id = get_stripe_customer_id(self.request.user)
        return get_all_payment_methods_of_user(stripe_customer_id).data


class DeattachPaymentMethodOfUser(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def delete(self, request, *args, **kwargs):
        payment_method_id = kwargs.get('payment_method_id')
        deatach_payment_method_of_user(payment_method_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetSubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self,request,*args, **kwargs):
        subscription_id = kwargs.get("subscription_id")
        if not subscription_id:
            raise ValidationError("subscription id must be provided")

        if Subscription.objects.filter(customer=request.user, stripe_subscription_id=subscription_id):
            data = get_subscription_detail(subscription_id)
            return Response(data=data)
        raise ValidationError("No stripe subscription found against user")
