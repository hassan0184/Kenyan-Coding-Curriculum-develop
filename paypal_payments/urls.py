from django.urls import path
from .views import (
    GetClientToken, GetAllPlans, CreateSubscriptionView,
     GetAllSubscriptionsForPlan, SavePaymentMethodView,
      ListPaymentMethodView, CancelPaypalSubscriptionView,
      ListPaymentMethodView,UpgradeSubscriptionView)


urlpatterns = [
    path('client/token', GetClientToken.as_view(),name="get-client-token"), 
    path('plans', GetAllPlans.as_view(),name="get-all-plans"),
    path("subscription",CreateSubscriptionView.as_view(), name="create-subscription"),
    path("subscription/cancel",CancelPaypalSubscriptionView.as_view(), name="cancel-subscription"),
    path("subscription/upgrade",UpgradeSubscriptionView.as_view(), name="upgrade-subscription"),
    path("plans/subscriptions",GetAllSubscriptionsForPlan.as_view(),name="get-all-subscriptions-for-plan"),
    path("method/",SavePaymentMethodView.as_view(),name="save-payment-method"),
    path("method",ListPaymentMethodView.as_view(),name="get-all-payment-methods"),
    
]

