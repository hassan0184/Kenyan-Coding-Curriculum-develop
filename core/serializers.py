import os
from rest_framework import serializers
from .models import School, Class, Grade, Post, RequestQoute,RequestedSchool
from common_utilities.send_mail import SendEmail
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class RequestSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedSchool
        fields=['name','type','district']
    def create(self, validated_data):
        validated_data['requested_teacher'] = self.context['request'].user
        return super(RequestSchoolSerializer, self).create(validated_data=validated_data)


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'    

    
class RequestQouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestQoute
        fields = "__all__"
        
    def save(self, **kwargs):
        super().save(**kwargs)
        description = self.validated_data.get("description")
        name = self.validated_data.get("name")
        email = self.validated_data.get("email")
        phone = self.validated_data.get("phone")
        title = self.validated_data.get("title")
        description =description + f"""
        name->  {name}
        email-> {email}
        phone-> {phone}
        title -> {title}
        """
        data = {
            "to_email":os.environ.get("EMAIL_FROM"),
            "body":description,
            "email_subject":"Request Quote"
        }
        SendEmail.send_email(data)

