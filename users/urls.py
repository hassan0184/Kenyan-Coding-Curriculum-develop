from django.urls import path
from .views import (
    TeacherLoginView,
    TeacherRegisterationView,
    StudentLoginView,
    StudentRegisterationView,
    StudentUserNameCheckView,
    UploadStudentRegistrationView,
    SendPasswordResetEmailView,
    TeacherPasswordResetView,
    TeacherChangePasswordView,
    SendTeacherAccountConfirmationOTPView,
    TeacherAccountConfirmationOTPView,
    TeacherView,
    TeacherOverviewPageGetDataView,
    StudentListView,
    StudentRetrieveUpdateDeleteView,
    StudentOverviewPageGetDataView,
    FakeDataView,
    StudentView,
    GetStudentsCSVView,
    GetMySubscriptionDetails,
    CancelMySubscription,)
from core.views import RequestQouteView


urlpatterns = [
    path('teachers/login/', TeacherLoginView.as_view(), name="teacher-login"),
    path('teachers/register/', TeacherRegisterationView.as_view(),
         name='teacher-registeration'),
    path('teachers/reset/password/send/mail/',
         SendPasswordResetEmailView.as_view(), name='teacher-registeration'),
    path('teachers/reset/password/',
         TeacherPasswordResetView.as_view(), name="reset-password"),
    path('teachers/me/change/password/',
         TeacherChangePasswordView.as_view(), name="change-password"),
    path('teachers/me/send/otp/',
         SendTeacherAccountConfirmationOTPView.as_view(), name="send-otp"),
    path('teachers/me/confirm/otp/',
         TeacherAccountConfirmationOTPView.as_view(), name="verify-otp"),
    path('teachers/me/', TeacherView.as_view(), name="teacher"),
    path('teachers/me/subscription', GetMySubscriptionDetails.as_view(), name="my-subscription"),
    path('teachers/me/subscription/cancel', CancelMySubscription.as_view(), name="cancel-my-subscription"),
    path("teachers/request/quote", RequestQouteView.as_view(), name="request-quoute"),
    
    
    path('students/me/', StudentView.as_view(), name="studentMe"),
    path('students/login/', StudentLoginView.as_view(), name='student-login'),
    path('students/register/', StudentRegisterationView.as_view(),
         name='student-registeration'),
    path('students/username/check', StudentUserNameCheckView.as_view(),
         name='student-username-check'),     
    path('students/register/upload', UploadStudentRegistrationView.as_view(),
         name='student-upload'),
    path('students/class/<int:id>/', StudentListView.as_view(), name="students-of-class"),
    path('students/class/<int:id>/csv', GetStudentsCSVView.as_view(), name="students-csv"),
    path('students/<int:pk>/', StudentRetrieveUpdateDeleteView.as_view(),
         name="update-delete-retrive-student"),
    path("teachers/me/classes/<int:class_id>/overview",
         TeacherOverviewPageGetDataView.as_view(), name="teacher-overview-page"),
    path("students/me/overview", StudentOverviewPageGetDataView.as_view(),
         name="student-overview"),
     
    path("data/", FakeDataView.as_view(), name="fake-view"),
]
