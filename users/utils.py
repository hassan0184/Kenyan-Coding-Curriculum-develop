from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from paypal_payments.choices import SubscriptionStatus as PaypalSubscriptionStatus
from django.contrib.auth import authenticate
import stripe
from .models import Student, Teacher
from rest_framework.exceptions import NotFound
from sripe_payments.models import StripeCustomer, Subscription
from paypal_payments.models import PaypalCustomer, PaypalSubscription
from paypal_payments.utils import (
    cancel_subscription as cancel_paypal_subscription,
    get_subscription_id_for_customer as get_paypal_subscription_id,
    number_of_saved_paypal_payment_methods
)
from sripe_payments.utils import (
    cancel_subscription as cancel_stripe_subscription,
    get_subscription_id_for_customer as get_stripe_subscription_id,
    number_of_saved_stripe_payment_methods,
)


def register_teacher(serializer, success_msg: str = "Registeration success."):
    if serializer.is_valid(raise_exception=True):
        teacher = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def register_student(serializer, success_msg: str = "Registeration success."):
    if serializer.is_valid(raise_exception=True):
        student = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login_teacher(request, format=None):
    email = request.data.get("email")
    password = request.data.get("password")
    email = email.lower()
    data = login_teacher_using_email_password(email, password)
    return Response(data, status=status.HTTP_200_OK)

    
def login_teacher_using_email_password(email, password, throw_exception=True, is_password_encrypted=False):
    if email is None:
        raise ValidationError('Email should not be empty')
    if password is None:
        raise ValidationError('Password should not be empty')
    user = authenticate(username=email, password=password)
    if user is not None:
        data = get_access_and_refresh_token_for_teacher(user)
        return data
    else:
        if throw_exception:
            raise ValidationError('Invalid login credentials')
    return False


def get_access_and_refresh_token_for_teacher(teacher):
    if teacher is not None:
        refresh = RefreshToken.for_user(teacher)
        data = {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customizes JWT default Serializer to add more information about user"""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        return super().validate(attrs)


# def login_student(request, format=None):
#     email = request.data.get("email", None)
#     password = request.data.get("password", None)
#     if email is None:
#         raise ValidationError('email should not be empty')
#     if password is None:
#         raise ValidationError('Password should not be empty')

#     student = authenticate_student(email=email, password=password)
#     if student is not None:
#         token = CustomTokenObtainPairSerializer.get_token(student)
#         data = {
#             'refresh_token': str(token),
#             'access_token': str(token.access_token)
#         }
#         return Response(data, status=status.HTTP_200_OK)
#     else:
#         raise ValidationError('Invalid login credentials')


# def authenticate_student(email, password):
#     '''gets the students useremail and password and return the student
#     based on credentials and None if credentials are invalid.'''
#     student = Student.objects.filter(
#         email=email, password=password).first()
#     if student is not None:
#         return student
#     return None


def login_student(request, format=None):

    '''check the students username and password are valid or not!'''

    username = request.data.get("username", None)
    password = request.data.get("password", None)
    if username is None:
        raise ValidationError('email should not be empty')
    if password is None:
        raise ValidationError('Password should not be empty')

    student = authenticate_student(username=username, password=password)
    if student is not None:
        token = CustomTokenObtainPairSerializer.get_token(student)
        data = {
            'refresh_token': str(token),
            'access_token': str(token.access_token)
        }
        return Response(data, status=status.HTTP_200_OK)
    else:
        raise ValidationError('Invalid login credentials')







def authenticate_student(username, password):
    '''gets the students username and password and return the student
    based on credentials and None if credentials are invalid.'''
    student = Student.objects.filter(
        username=username, password=password).first()
    if student is not None:
        return student
    return None


def send_verfication_code(teacher: Teacher, counter: int, change_time):
    pass


def check_teacher_is_having_given_class_or_not_found_exception(teacher: Teacher, class_id):
    if not teacher.classes.filter(pk=class_id):
        raise NotFound(f"teacher is not having any class with id {class_id}")



def get_user_subscription_type(local_user):
    '''
    returns subscription type at 0th index
    and gateway at 1th index.
    '''
    subscription, gateway = "Free", None
    paypal_subscription_obj = PaypalSubscription.objects.filter(local_customer=local_user).first()
    stripe_subscription_obj = Subscription.objects.filter(customer=local_user).first()
    
    if paypal_subscription_obj:
        if paypal_subscription_obj.subscription_status == PaypalSubscriptionStatus.ACTIVE: 
            subscription, gateway = "Premium", "Paypal"
            return subscription, gateway
    if stripe_subscription_obj:
        if stripe_subscription_obj.subscription_status == "active":
            subscription, gateway = "Premium", "Stripe"
            return subscription, gateway
    

    if number_of_saved_stripe_payment_methods(local_user):
        gateway = "Stripe"
        return subscription, gateway
    
    if number_of_saved_paypal_payment_methods(local_user):
        gateway = "Paypal"
        return subscription, gateway
    


    return subscription, gateway


def cancel_user_subscription(local_user):
    subscription_type = get_user_subscription_type(local_user)
    if subscription_type == "Paypal Premium":
        paypal_subscription_id = get_paypal_subscription_id(local_user)
        cancel_paypal_subscription(paypal_subscription_id)
    elif subscription_type == "Stripe Premium":
        stripe_subscription_id = get_stripe_subscription_id(local_user.id)
        cancel_stripe_subscription(stripe_subscription_id)
        