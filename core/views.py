from django.shortcuts import render
from .serializers import PostSerializer, SchoolSerializer, ClassSerializer, GradeSerializer, RequestQouteSerializer,RequestSchoolSerializer
from .models import Grade, School, Class, Post
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from common_utilities.utils import get_object_or_not_found_exception
from users.permissions import IsStudent, IsTeacher
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView,
    ListAPIView, CreateAPIView,
)


class SchoolListCreateView(ListCreateAPIView):
    serializer_class = SchoolSerializer
    queryset = School.objects.all()

class RequestSchoolCreateView(CreateAPIView):
    serializer_class = RequestSchoolSerializer

class ClassListCreateView(ListCreateAPIView):
    serializer_class = ClassSerializer
    queryset = Class.objects.all()

    def post(self, request, *args, **kwargs):
        request.data['teacher'] = request.user.id
        try:
            request.data['school'] = request.user.school.id
        except:
            raise NotFound(
                f"You cannot add any class for the Teacher {request.user.first_name} as there is no school for him.")
        return super().post(request, *args, **kwargs)


class ClassDetaillView(RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_class_object(self, pk):
        try:
            return Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            error = get_object_or_not_found_exception(
                Class, pk, "No Class found with given id.")

    def get_object(self):
        class_id = self.kwargs.get('pk')
        return self.get_class_object(class_id)


class GradeListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = GradeSerializer
    queryset = Grade.objects.all()


class PostListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class RequestQouteView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = RequestQouteSerializer