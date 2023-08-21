from django.urls import path
from .views import (
    SchoolListCreateView,
    RequestSchoolCreateView,
    ClassListCreateView,
    ClassDetaillView,
    GradeListView,
    PostListView,
)

urlpatterns = [
    path('schools/', SchoolListCreateView.as_view(), name="schools"),
    path('requestschools/', RequestSchoolCreateView.as_view(), name="schools"),
    path('class/', ClassListCreateView.as_view(), name="class"),
    path('class/<int:pk>', ClassDetaillView.as_view(),
         name="class-details"),
    path("grads",GradeListView.as_view(),name="grade-list"),
    path("posts",PostListView.as_view(),name="post-list"),
]
