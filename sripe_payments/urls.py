from django.urls import path
from .views import (
    CreateSubscriptionView,
    subscription_update_webhook,
    GetStripePublicKeyView,
    GetAllStripeProductsView,
    GetFakePaymentMethodId,
    SaveCardView,
    GetAllCardsOfUserView,
    DeattachPaymentMethodOfUser,
    CancelSubscriptionView,
    GetSubscriptionDetailView,
    UpdateSubscriptionView,
)

urlpatterns = [
    path("subscription",CreateSubscriptionView.as_view(), name="create-subscription"),
    path("subscription/me",GetSubscriptionDetailView.as_view(), name="get-subscription-detail"),
    path("subscription/cancel",CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path("subscription/upgrade",UpdateSubscriptionView.as_view(), name="create-subscription"),
    path("subscription/webhook/subscription/update",subscription_update_webhook, name="create-subscription"),
    path("publickey",GetStripePublicKeyView.as_view(), name="get-public-key"),
    path("get-all-products",GetAllStripeProductsView.as_view(),name="get-all-products"),
    path("payment_method/fake",GetFakePaymentMethodId.as_view(),name="get-fake-payment-method-id"),
    path("cards/save",SaveCardView.as_view(),name="save-customer-card"),
    path("cards",GetAllCardsOfUserView.as_view(),name="get-all-cards"),
    path("payment_methods/<str:payment_method_id>",DeattachPaymentMethodOfUser.as_view(),name="remove-card"),
]
