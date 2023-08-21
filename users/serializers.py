import os
import re
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken
import pyotp
from common_utilities.otp import generate_otp, verify_otp
from common_utilities.send_mail import SendEmail
from .models import (Teacher, Student)
from .models import Teacher, Student
from .utils import get_access_and_refresh_token_for_teacher, get_user_subscription_type, get_paypal_subscription_id, \
    get_stripe_subscription_id
from sripe_payments.utils import get_subscription_detail as get_stripe_subscription_detail
from paypal_payments.utils import get_subscription_detail as get_paypal_subscription_detail
from core.serializers import ClassSerializer, GradeSerializer, PostSerializer, SchoolSerializer
from core.models import School, Post
from common_utilities.send_mail import SendEmail


class TeacherRegisterationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Teacher
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, email):
        return email.lower()

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise ValidationError(
                "Password and Confirm Password doesn't match.")
        return attrs

    def create(self, validated_data):
        secret_key = pyotp.random_base32()
        otp = generate_otp(secret_key)
        data = {
            'email_subject': "Edmazing Account Confirmation",
            'body': f"""
            your account activation password is {otp}
            """,
            'to_email': f'{validated_data.get("email")}'
        }
        SendEmail.send_email(data)
        teacher = Teacher.objects.create_user(**validated_data)
        teacher.secret_key = secret_key
        teacher.save()
        return teacher

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        data = get_access_and_refresh_token_for_teacher(instance)
        representation['access_token'] = data.get('access_token')
        representation['refresh_token'] = data.get('refresh_token')
        return representation


class StudentRegisterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['email', 'name', 'username', 'password', 'clas']
        extra_kwargs = {
            'password': {'write_only': False, 'read_only': False}
        }

    def validate_username(self, username):
        total_length = len(username)
        digit_length = len(re.findall("\d", username))
        character_length = len(re.findall("\D", username))
        if total_length >=8 and digit_length == 2 and character_length >=6:
              return username
        

        else:
            raise ValidationError(
                "Not follow the rules to create username")

    def validate_clas(self, clas):
        if clas.no_of_students <= clas.students.all().count():
            raise ValidationError(
                "There is no room in this class anymore, Please upgrade your plan")
        return clas

    def create(self, validated_data):
        return Student.objects.create_student(**validated_data)


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if not Teacher.objects.filter(email=email).exists():
            raise ValidationError("You are not a registered user.")
        return attrs

    def create(self, attrs):
        email = attrs.get('email')
        teacher = Teacher.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(teacher.id))
        token = PasswordResetTokenGenerator().make_token(teacher)
        link = f""""\
            
            https://edmazingfrontend.herokuapp.com/confirm-reset-page?uid={uid}&token={token}/
        
        """
        body = f"""
            Click the following link to reset your passwrod \n{link}
        """
        data = {
            'email_subject': 'Reset your password',
            'body': body,
            'to_email': teacher.email
        }
        SendEmail.send_email(data)
        return attrs


class TeacherPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    uid = serializers.CharField(
        max_length=255, write_only=True)
    token = serializers.CharField(
        max_length=255, write_only=True)

    class Meta:
        fields = ['password', 'password2', 'uid', 'token']

    def validate(self, attrs):
        try:
            password = attrs.get("password", None)
            password2 = attrs.get("password2", None)
            token = attrs.get('token')
            uid = attrs.get('uid')
            uid = smart_str(urlsafe_base64_decode(uid))
            teacher = Teacher.objects.get(pk=uid)
            if not PasswordResetTokenGenerator().check_token(teacher, token):
                raise InvalidToken(
                    "Password reset token is not valid or expired")
            if password != password2:
                raise serializers.ValidationError(
                    "Password and Confirm password doesn't match.")
            if teacher.check_password(password):
                raise serializers.ValidationError("New password cannot be your current password.")
            teacher.set_password(password)
            teacher.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            raise InvalidToken("Password reset token is not valid or expired")


class ChangeTeacherPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password1 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password1', 'password2']

    def validate_password(self, password):
        teacher = self.context.get('request').user
        if not teacher.check_password(password):
            raise ValidationError("password is not correct.")
        return password

    def validate(self, attrs):
        password1 = attrs.get("password1", None)
        password2 = attrs.get("password2", None)
        if password1 != password2:
            raise serializers.ValidationError(
                "Password and Confirm password doesn't match.")
        if attrs.get('password') == password1:
            raise serializers.ValidationError("old password and new password cannot be the same.")
        return attrs

    def save(self, **kwargs):
        password1 = self.validated_data.get('password1', None)
        teacher = self.context.get('request').user
        teacher.set_password(password1)
        teacher.save()
        return teacher


class UsernameCheckerSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)

    def validate(self, attrs):
        username = attrs.get('username')
        username_available = "true"
        message = "Username available"
        if Student.objects.filter(username=username).exists():
            username_available = "false"
            message = "Username already exists"
        else:
            total_length = len(username)
            digit_length = len(re.findall("\d", username))
            character_length = len(re.findall("\D", username))
            if total_length < 8 or digit_length != 2 or character_length < 6:
                username_available = "false"
                message = "Incorrect username format"

        context = {"username_available": username_available,
                   "message": message}
        return context


class SendTeacherAccountConfirmationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)

    def validate_email(self, email):
        teacher = Teacher.objects.filter(email=email).first()
        if teacher:
            if not teacher.is_verified:
                return email
            else:
                raise ValidationError("Account is already verified.")
        else:
            raise ValidationError("email doesn't exist.")

    def validate(self, attrs):
        email = attrs.get('email')
        teacher = Teacher.objects.filter(email=email).first()
        attrs['teacher'] = teacher
        return attrs

    def save(self, **kwargs):
        teacher = self.validated_data.get('teacher')
        teacher.secret_key = pyotp.random_base32()
        teacher.save()
        otp = generate_otp(teacher.secret_key)
        data = {
            'email_subject': "Edmazing Account Confirmation",
            'body': f"""
            your account activation password is {otp}
            """,
            'to_email': f'{teacher.email}'
        }
        SendEmail.send_email(data)


class TeacherAccountConfirmationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)
    otp = serializers.CharField(max_length=255, write_only=True)

    def validate_email(self, email):
        teacher = Teacher.objects.filter(email=email).first()
        if teacher:
            if not teacher.is_verified:
                return email
            else:
                raise ValidationError("Account is already verified.")
        else:
            raise ValidationError("email doesn't exist.")

    def validate(self, attrs):
        email = attrs['email']
        attrs['teacher'] = Teacher.objects.filter(email=email).first()
        return attrs

    def save(self, **kwargs):
        teacher = self.validated_data.get('teacher')
        otp = self.validated_data.get('otp')
        if not verify_otp(teacher.secret_key, otp):
            raise ValidationError("Incorrect OTP")
        teacher.is_verified = True
        teacher.save()


class TeacherSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many=True)
    school_name = serializers.SerializerMethodField()
    subscription_type = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    subscription_id = serializers.SerializerMethodField()

    def get_subscription_type(self, teacher):
        return get_user_subscription_type(teacher)[0]

    def get_payment_method(self, teacher):
        subs_type, payment_method = get_user_subscription_type(teacher)
        return payment_method

    def get_subscription_id(self, teacher):
        subs_type, payment_method = get_user_subscription_type(teacher)
        subscription_id = None
        if subs_type == "Premium":
            if payment_method == "Paypal":
                subscription_id = get_paypal_subscription_detail(get_paypal_subscription_id(teacher)).get('id')
            elif payment_method == "Stripe":
                subscription_id = get_stripe_subscription_detail(get_stripe_subscription_id(teacher)).get('id')
            return subscription_id

    def get_school_name(self, teacher):
        if teacher.school:
            return teacher.school.name
        return None

    class Meta:
        model = Teacher
        fields = ['email', 'first_name', 'last_name', 'school', 'school_name', 'classes', 'subscription_type',
                  'payment_method', 'subscription_id']


class StudentSerializer(serializers.ModelSerializer):
    grade = serializers.CharField(source='clas.get_grade_level_display')
    class_name = serializers.CharField(source='clas.name')
    teacher_name = serializers.CharField(source="clas.teacher.get_full_name")
    school_name = serializers.SerializerMethodField()

    def get_school_name(self, student):
        return student.clas.school.name

    class Meta:
        model = Student
        fields = ['id', 'name', 'username', 'grade',
                  'password', 'class_name', "teacher_name", "clas", "school_name"]


class StudentSerializerAssignAssignment(serializers.ModelSerializer):
    grade = serializers.CharField(source='clas.get_grade_level_display')
    is_assigned = serializers.BooleanField()

    class Meta:
        model = Student
        fields = ['id', 'email', 'username',
                  'grade', 'password', 'is_assigned']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    class_ = serializers.IntegerField()


class StudentNameSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Student
        fields = ['id', 'username']
