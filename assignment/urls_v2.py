from django.urls import path, include
from .views import (
    GetTeksDetailsReportViewV2, AssignmentDetailViewV2,
     GetAttemptedAssignmentViewV2, GetTopicsForStudentViewV2
)

urlpatterns = [
    path('reports/teks/detail/classes/<int:class_id>',
         GetTeksDetailsReportViewV2.as_view(), name="get-teks-detail-report"),
    path("<int:pk>", AssignmentDetailViewV2.as_view(),
         name="assignment-detail"),
     path("students/me/attempted-assignments/<int:pk>",
         GetAttemptedAssignmentViewV2.as_view(), name="student-attempted-assignment-view"),
    path("students/me/topics", GetTopicsForStudentViewV2.as_view(),
         name='topics-for-student'),
]
