import csv
import re
import os
from botocore.exceptions import ClientError
from common_utilities import s3_utils
from io import StringIO
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from common_utilities.custom_generic_api_views import CustomCreateAPIView
from common_utilities.send_mail import SendEmail
from common_utilities.utils import serialize_data, build_url_for_file
from sripe_payments.utils import get_subscription_detail as get_stripe_subscription_detail
from paypal_payments.utils import get_subscription_detail as get_paypal_subscription_detail
from paypal_payments.utils import get_subscription_id_for_customer as get_paypal_subscription_id
from sripe_payments.utils import get_subscription_id_for_customer as get_stripe_subscription_id
from .utils import (register_teacher, register_student,
                    login_student, login_teacher,
    # username_checker,
                    check_teacher_is_having_given_class_or_not_found_exception,
                    get_user_subscription_type,
                    cancel_user_subscription)
from rest_framework.exceptions import ValidationError
from .serializers import (StudentRegisterationSerializer, StudentSerializer,

                          TeacherRegisterationSerializer,
                          SendPasswordResetEmailSerializer,
                          TeacherPasswordResetSerializer,
                          ChangeTeacherPasswordSerializer,
                          SendTeacherAccountConfirmationOTPSerializer,
                          TeacherAccountConfirmationOTPSerializer,
                          TeacherSerializer,
                          FileUploadSerializer,
                          UsernameCheckerSerializer,
                          )
from .permissions import IsStudent, IsTeacher
from common_utilities.utils import get_object_or_not_found_exception
from .models import Student, Class
from django.db.models import Q, F, Count, Sum, Avg
import pandas as pd
import logging
from assignment.utils import (get_completed_in_progress_not_started_assignments_of_class,
                              get_completed_in_progress_not_started_assignments_of_student)
from assignment.models import Assignment, AssignedAssignment, AssignmentResult
from assignment.serializers import AssignmentNameSerializer
from common_utilities.choices import AssignmentTypeChoices


class TeacherRegisterationView(CreateAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = TeacherRegisterationSerializer


class TeacherLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        return login_teacher(request)


class StudentRegisterationView(CreateAPIView):
    serializer_class = StudentRegisterationSerializer


class StudentUserNameCheckView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UsernameCheckerSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status.HTTP_200_OK)


class UploadStudentRegistrationView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = FileUploadSerializer

    def get_class_object(self, pk):
        try:
            return Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            error = get_object_or_not_found_exception(
                Class, pk, "No Class found with given id.")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        class_ = serializer.validated_data['class_']
        class_obj = self.get_class_object(class_)

        reader = pd.read_csv(file)
        header = ['username', 'name', 'password', 'creation', 'error']

        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for _, row in reader.iterrows():
            try:
                student = Student(
                    name=row["name"],
                    username=row['username'],
                    clas=class_obj,
                    password=row["password"]
                )
            except KeyError as key_error:
                raise ValidationError(f"{key_error} not found in the csv.")
            output_row = [student.username, student.name, row['password'], ]
            try:
                student.save()
                output_row.append("Success")
                writer.writerow(output_row)
            except Exception as e:
                output_row.append("Failed")
                if e.__class__.__name__ == "IntegrityError":
                    output_row.append("duplicate username or email found")
                writer.writerow(output_row)
        data = {}
        data['to_email'] = request.user.email
        data["email_subject"] = "Student Registeration Details"
        data["body"] = "check the file below for student registeration details."

        SendEmail.send_email(data=data, filename='students.csv', file=csv_file)
        return Response({"status": "success"},
                        status.HTTP_201_CREATED)


class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        return login_student(request)


class SendPasswordResetEmailView(CustomCreateAPIView):
    status = status.HTTP_200_OK
    serializer_class = SendPasswordResetEmailSerializer
    permission_classes = [AllowAny]


class TeacherChangePasswordView(CustomCreateAPIView):
    status = status.HTTP_200_OK
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = ChangeTeacherPasswordSerializer


class TeacherPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = TeacherPasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendTeacherAccountConfirmationOTPView(CustomCreateAPIView):
    permission_classes = [AllowAny]
    status = status.HTTP_200_OK
    serializer_class = SendTeacherAccountConfirmationOTPSerializer


class TeacherAccountConfirmationOTPView(CustomCreateAPIView):
    status = status.HTTP_200_OK
    serializer_class = TeacherAccountConfirmationOTPSerializer
    permission_classes = [AllowAny]


class FakeDataView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        return Response({"data": "alots of data"})


class TeacherView(RetrieveUpdateAPIView):
    serializer_class = TeacherSerializer

    def get_object(self):
        return self.request.user


class StudentView(RetrieveUpdateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_object(self):
        return self.request.user


class StudentListView(ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['username', 'email']
    search_fields = ['username', 'email']

    def get_queryset(self):
        class_id = self.kwargs.get('id')
        return Student.objects.all_in_class(class_id).order_by('username')


class GetStudentsCSVView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        class_id = kwargs.get('id')
        get_object_or_not_found_exception(Class, class_id)
        query_set = Student.objects.filter(clas=class_id).values_list('username', 'email', 'password').order_by(
            'username')
        print(query_set)
        df = pd.DataFrame(query_set, columns=['username', 'email', 'password'])
        df.to_excel('output.xlsx', engine='xlsxwriter')
        try:
            response = s3_utils.upload_file_to_s3('output.xlsx', "students_csv.xlsx")
        except ClientError as e:
            logging.error(e)
        os.remove('output.xlsx')
        link = s3_utils.get_file_url('students_csv.xlsx')
        return Response({"student_details_csv_link": link})


class StudentRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsTeacher]


class TeacherOverviewPageGetDataView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, format=None, **kwargs):
        class_id = kwargs.get('class_id')
        students = request.user.get_all_students_of_class(class_id)
        student_serializer = StudentSerializer(data=students, many=True)
        student_serializer.is_valid()
        # AssignedAssignment.objects.
        assigned_assignments_of_class = AssignedAssignment.objects.filter(
            _class=class_id, assignment__in=Assignment.objects.get_all_assignments_of_class(class_id))
        # ---------------------
        # all_assigned_assignments_of_class = Assignment.objects.filter(pk__in = AssignedAssignment.objects.filter(_class=class_id, assignment__in =assignments_of_class).values_list('assignment') )
        completed_assignments, in_progress_assignments, not_started_assignments = get_completed_in_progress_not_started_assignments_of_class(
            class_id)
        no_of_skills_assignments_completed = completed_assignments.filter(
            _type=AssignmentTypeChoices.ASSESMENT_BY_SKILLS).count()
        results_with_percentage = AssignmentResult.objects.filter(
            assignment__in=completed_assignments, student__in=students).annotate(
            percentage=F('marks_obtained') / F('assignment__marks'))

        group_by_students = results_with_percentage.values('student').annotate(
            average=Avg('percentage') * 100)

        if group_by_students:
            class_average = (group_by_students.filter(
                average__gte=70).count() / group_by_students.count()) * 100
        else:
            class_average = None
        # critical teks
        critical_assignments = Assignment.objects.filter(
            pk__in=results_with_percentage.annotate(_class=F('student__clas')).values('assignment', '_class').annotate(
                average=Avg('percentage') * 100).filter(average__gte=70).values('assignment'))

        recomended_assignments = Assignment.objects.filter(
            pk__in=results_with_percentage.annotate(_class=F('student__clas')).values('assignment', '_class').annotate(
                average=Avg('percentage') * 100).filter(average__lt=70).values('assignment'))

        critical_assignments_serializer = AssignmentNameSerializer(data=critical_assignments, many=True)
        critical_assignments_serializer.is_valid()
        recomended_assignments_serializer = AssignmentNameSerializer(data=recomended_assignments, many=True)
        recomended_assignments_serializer.is_valid()

        completed_assignments_serializer = AssignmentNameSerializer(
            data=completed_assignments, many=True)
        completed_assignments_serializer.is_valid()
        in_progress_assignments_serializer = AssignmentNameSerializer(
            data=in_progress_assignments, many=True)
        in_progress_assignments_serializer.is_valid()
        not_started_assignments_serializer = AssignmentNameSerializer(
            data=not_started_assignments, many=True)
        not_started_assignments_serializer.is_valid()

        data = {}
        data['students'] = student_serializer.data
        data['completed_assignments'] = completed_assignments_serializer.data
        data['not_started_assignments'] = not_started_assignments_serializer.data
        data['in_progress_assignments'] = in_progress_assignments_serializer.data
        data['no_of_skills_assignments_completed'] = no_of_skills_assignments_completed
        data['class_average'] = class_average
        data['critical_assignments'] = critical_assignments_serializer.data
        data['recomended_assignments'] = recomended_assignments_serializer.data
        assignments_of_class = Assignment.objects.get_all_assignments_of_class(
            class_id)
        assignments = Assignment.objects.all()
        assigment_serializer = AssignmentNameSerializer(
            data=assignments, many=True)
        assigment_serializer.is_valid()
        all_assigned_assignments_of_class = AssignedAssignment.objects.filter(
            _class=class_id, assignment__in=assignments_of_class).values_list('assignment')

        return Response(data)


class StudentOverviewPageGetDataView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, **kwargs):
        data = {}
        assignments = get_completed_in_progress_not_started_assignments_of_student(self.request.user.id)
        data['completed_assignments'] = serialize_data(AssignmentNameSerializer, data=assignments[0], many=True)
        data['in_progress_assignments'] = serialize_data(AssignmentNameSerializer, data=assignments[1], many=True)
        data['not_started_assignments'] = serialize_data(AssignmentNameSerializer, data=assignments[2], many=True)

        data['student'] = serialize_data(StudentSerializer, instance=self.request.user)
        # recomended assignments
        completed_assignments = assignments[0]
        recomended_assignment_list = AssignmentResult.objects.filter(
            assignment__in=completed_assignments, student=request.user.id).annotate(
            percentage=F('marks_obtained') / F('assignment__marks')).filter(percentage__lt=0.7).values('assignment')

        recomended_assignemts = Assignment.objects.filter(pk__in=recomended_assignment_list)
        data['recomended_assignments'] = serialize_data(AssignmentNameSerializer, data=recomended_assignemts, many=True)
        return Response(data=data)


class GetMySubscriptionDetails(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, *args, **kwargs):
        subscription_id = None
        subscription = {
            "id": None,
            "status": "None",
            "price": "0.00",
            "expiry_date": None,
            "renewal_date": None
        }

        subs_type, payment_method = get_user_subscription_type(request.user)
        if subs_type == "Premium":
            if payment_method == "Paypal":
                subscription = get_paypal_subscription_detail(get_paypal_subscription_id(request.user))
            elif payment_method == "Stripe":
                subscription = get_stripe_subscription_detail(get_stripe_subscription_id(request.user))
        return Response(data={'subscription': subscription})


class CancelMySubscription(APIView):
    def post(self, request, *args, **kwargs):
        cancel_user_subscription(self.request.user)
        return Response(data={"msg": "You won't be charged again"})
