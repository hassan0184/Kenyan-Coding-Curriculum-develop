from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from .serializers import CreatePaypalSubscriptionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from common_utilities.utils import get_value_from_dict_or_bad_request
from .serializers import SavePaymentMethodSerializer, PaymentMethodSerializer, CancelPaypalSubscriptionSerializer, UpgradeSubscriptionSerializer
from .utils import  (
    get_client_token, 
    create_customer,
    get_all_plans,
    create_subscription,
    create_subscription_for_user,
    get_all_subscription_for_a_plan,
    serializer_subscription,
    save_payment_method,
    get_customer_from_local_customer_id,
    get_paypal_customer_id_from_local_customer,
    get_all_payment_methods,)
# Create your views here.

class GetClientToken(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        local_customer = request.user
        create_customer(local_customer.first_name, local_customer.last_name,local_customer.email,local_customer=local_customer)
        return Response(data={"client_token":get_client_token(local_customer.id)})


class GetAllPlans(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(data = {"plans":get_all_plans()})



class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        validation_serialzier = CreatePaypalSubscriptionSerializer(data=request.data)
        validation_serialzier.is_valid(raise_exception=True)
        create_customer(request.user.first_name,request.user.last_name,request.user.email, request.user)
        result = create_subscription_for_user(request.user.id,request.data.get("plan_id"),request.data.get("payment_method_nounce"))
        if result.is_success:
            return Response(data={"subscription":serializer_subscription(result.subscription)})
        return Response(data={result.message})


class GetAllSubscriptionsForPlan(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args,**kwargs):
        return Response(data={"subscriptions":get_all_subscription_for_a_plan("cs32")})



class SavePaymentMethodView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavePaymentMethodSerializer


class ListPaymentMethodView(ListAPIView):

    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        paypal_customer_id = get_paypal_customer_id_from_local_customer(self.request.user)
        if paypal_customer_id:
            return get_all_payment_methods(paypal_customer_id)


class CancelPaypalSubscriptionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CancelPaypalSubscriptionSerializer


class UpgradeSubscriptionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpgradeSubscriptionSerializer


