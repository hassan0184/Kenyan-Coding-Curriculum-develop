from re import sub
from django.db.models import Count, Case, When, IntegerField
from django.utils import timezone
from django.db.models import Count, Q
from common_utilities.choices import GradeLevelChoices, AssignmentTypeChoices
from users.models import Student
from .utils import create_assignment_result_from_assignment_result_details
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from .serializers import (
    AssignmentSerializer, ResultSerializer, TopicSerializer,
    TopicNameSerializer, AssignmentNameSerializer,
    AssignedAssignmentSerializer, AssignmentResultDetailSerializer,
    ShowResultDetailAssignmentSerializer, StudentCompetencyReportSerialzier,
    TeksDetailReportSerializer, GrowthByTeksReportSerializer,
    AssignedAssignmentListSerializer, AssignedAssignmentSerializer2,
    AssignedAssignmentUpdateSerializer,WorksheetDownloadSerializer,
    AssignmentDetailResultSerializer, AssignmentSerializer2,
    AssignmentSerializerVersion2, SubmittedAssignmentSerializerVersion2,
    TestQuestionSerializer
    )
from .models import AssignedAssignment, Assignment, AssignmentResult, AssignmentResultDetail, Topic, TestQuestion
from core.models import Class
from assignment.models import Assignment
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStudent, IsTeacher
from common_utilities.utils import get_object_or_not_found_exception
from users.serializers import StudentSerializer, StudentSerializerAssignAssignment
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound, MethodNotAllowed
from common_utilities.utils import get_value_or_bad_request_exception, get_object_or_not_found_exception, insert_assignment_result_detail
from django.db.models import Q, F, Sum, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny


class AssignmentListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['_type']

    def get_serializer_class(self):
        if 'names' in self.request.path:
            return AssignmentNameSerializer
        return AssignmentSerializer

    def get_queryset(self):
        topic_id = self.kwargs.get('topic_id')
        topic = get_object_or_not_found_exception(
            Topic, topic_id, "No Topic found with given id.")
        return Assignment.objects.filter(topic=topic_id)


class TopicListView(ListAPIView):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        clas = get_object_or_not_found_exception(
            Class, class_id, "No class found with given id.")
        return Topic.objects.filter(grade=clas.grade_level)


class TopicNameListView(ListAPIView):
    serializer_class = TopicNameSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        clas = get_object_or_not_found_exception(
            Class, class_id, "No class found with given id.")
        return Topic.objects.filter(grade=clas.grade_level)


class StudentAssignmentListView(ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        assignment_id = self.kwargs.get('assignment_id')
        AssignedAssignment.objects.filter(assignment=assignment_id)


class AssignAssignmentCreateView(CreateAPIView):
    serializer_class = AssignedAssignmentSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['assign_to_entire_class'] = get_value_or_bad_request_exception(
            self.request.data, "assign_to_entire_class")
        return context


class StudentAssignedAssignmentsListView(ListAPIView):
    serializer_class = AssignedAssignmentSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return AssignedAssignment.objects.filter(student=self.request.user)


class AssignAssignmentGetAllStudentsView(ListAPIView):
    serializer_class = StudentSerializerAssignAssignment
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        class_ = get_value_or_bad_request_exception(self.kwargs, 'class_id')
        class_ = get_object_or_not_found_exception(Class, class_)
        assignment = get_value_or_bad_request_exception(
            self.kwargs, 'assignment_id')
        assignment = get_object_or_not_found_exception(Assignment, assignment)
        if not self.request.user.classes.filter(pk=class_.pk).first():
            raise NotFound("no given foud for given teacher")
        return AssignedAssignment.objects.get_all_students_of_a_class_wrt_assignment(self.request.user, class_.pk, assignment.pk)


class AssignmentDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializer2
    queryset = Assignment.objects.all()


class AssignmentDetailViewV2(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializerVersion2
    queryset = Assignment.objects.all()


class SubmitAssignmentView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = AssignmentResultDetailSerializer


    def post(self, request, *args, **kwargs):
        assignment_id = kwargs.get('assignment_id')
        if AssignmentResult.objects.filter(student=request.user.id,assignment=assignment_id):
            raise ValidationError("You have submitted this assignment before.")

        with transaction.atomic():
            assignment_obj = get_object_or_not_found_exception(Assignment, assignment_id)
            
            total_marks_obtained_mcqs = 0
            if request.data.get("mcq_questions"):
                for mcq_question in request.data.get('mcq_questions'):
                    assignment_result_detail = insert_assignment_result_detail({"assignment": assignment_obj.id,"student":request.user.id,"mcq_question": mcq_question.get("id"),"mcq_selected_options":mcq_question.get("mcq_selected_options")}, AssignmentResultDetailSerializer)
                    total_marks_obtained_mcqs += assignment_result_detail.mcq_question.get_obtained_marks(assignment_result_detail.mcq_selected_options.all())

            total_marks_obtained_fraction_model_1_questions = 0
            if request.data.get("fraction_model_1"):
                for fraction_model_1_question in request.data.get("fraction_model_1"):
                    marked_indexes = fraction_model_1_question.get("marked_indexes")
                    if marked_indexes:
                        marked_indexes = str(marked_indexes)[1:-1]
                        assignment_result_detail = insert_assignment_result_detail({"assignment": assignment_obj.id,"student":request.user.id,"fraction_model_1_question": fraction_model_1_question.get("id"),"fraction_model_1_answers":marked_indexes}, AssignmentResultDetailSerializer)
                        total_marks_obtained_fraction_model_1_questions += assignment_result_detail.fraction_model_1_question.get_obtained_marks(marked_indexes)

            total_marks_obtained_sorting_questions = 0
            if request.data.get("sorting_questions"):
                for sorting_question in request.data.get('sorting_questions'):
                    assignment_result_detail = insert_assignment_result_detail({"assignment": assignment_obj.id,"student": request.user.id,"sorting_question" : sorting_question.get("id"), "sorting_question_selected_options" : sorting_question.get("selected_answers")},AssignmentResultDetailSerializer)
                    total_marks_obtained_sorting_questions += assignment_result_detail.sorting_question.get_obtained_marks(assignment_result_detail.sorting_question_selected_options.all())   

            
            total_marks_obtained_fill_in_the_blanks = 0
            if request.data.get("fill_in_the_blank_questions"):
                for fill_the_blank_question in request.data.get('fill_in_the_blank_questions'):
                    assignment_result_detail = insert_assignment_result_detail({"assignment": assignment_obj.id,"student": request.user.id,"fill_in_the_blank_question" : fill_the_blank_question.get("id"), "fill_in_the_blank_question_answers" : fill_the_blank_question.get("selected_answers")},AssignmentResultDetailSerializer)
                    total_marks_obtained_fill_in_the_blanks += assignment_result_detail.fill_in_the_blank_question.get_obtained_marks(assignment_result_detail.fill_in_the_blank_question_answers.all())
            
            
            # if request.data.get("drop_down_questions"):
            #     for drop_down_question in request.data.get('drop_down_questions'):
            #         assignment_result_detail_serialzier = AssignmentResultDetailSerializer(data={"assignment": assignment_obj.id,"student": request.user.id, "drop_down_question": drop_down_question.get("id"),"drop_down_selected_option" : drop_down_question.get("selected_option")})
            #         assignment_result_detail_serialzier.is_valid(raise_exception=True)
            #         assignment_result_detail_serialzier.save()

            # if request.data.get("calculator_questions"):
            #     for calculator_question in request.data.get('calculator_questions'):
            #         assignment_result_detail_serialzier = AssignmentResultDetailSerializer(data={"assignment": assignment_obj.id,"student": request.user.id,"calculator_question" : calculator_question.get("id"),"calculator_question_answer": calculator_question.get("answer")})
            #         assignment_result_detail_serialzier.is_valid(raise_exception=True)
            #         assignment_result_detail_serialzier.save()

            


            # assignment_result_obj = create_assignment_result_from_assignment_result_details(assignment_id, request.user)
            marks_obtained = (total_marks_obtained_fraction_model_1_questions + total_marks_obtained_mcqs + total_marks_obtained_sorting_questions + total_marks_obtained_fill_in_the_blanks)
            assignment_result_obj = AssignmentResult(assignment=assignment_obj, student=request.user, marks_obtained=marks_obtained)
            assignment_result_obj.save()

        return Response(data={"Assignment submitted successfully."})


class SubmitAssignmentViewV2(CreateAPIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        assignment_id = kwargs.get('assignment_id')
        if AssignmentResult.objects.filter(student=request.user.id,assignment=assignment_id):
            raise ValidationError("You have submitted this assignment before.")

        





class GetTopicsForStudentView(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = TopicNameSerializer

    def get_queryset(self):
        topics = None
        assignments = None
        if 'current' in self.request.query_params:
            if self.request.query_params['current'] == "True":
                required_assignments = AssignedAssignment.objects.filter(students=self.request.user, from_date__lte=timezone.now(
                ), to_date__gt=timezone.now()).values('assignment')
                submitted_assignments = AssignmentResult.objects.filter(assignment__in= required_assignments).values('assignment')
                required_assignments = required_assignments.exclude(assignment__in = submitted_assignments)
                topics = AssignedAssignment.objects.filter(students=self.request.user, from_date__lte=timezone.now(
                ), to_date__gt=timezone.now()).values('assignment__topic')

                return Topic.objects.filter(pk__in=topics).annotate(total_assignments=Count(Case(
                    When(assignments__in=required_assignments, then=1),output_field=IntegerField(),)))

            else:
                required_assignments = AssignedAssignment.objects.filter(students=self.request.user, from_date__lt=timezone.now(
                ), to_date__lte=timezone.now()).values('assignment') 
                topics = AssignedAssignment.objects.filter(students=self.request.user, from_date__lt=timezone.now(
                ), to_date__lte=timezone.now()).values('assignment__topic')
                return  Topic.objects.filter(pk__in=topics).annotate(total_assignments=Count(Case(
                When(assignments__in=required_assignments, then=1),output_field=IntegerField(),)))
        else:
            required_assignments = AssignedAssignment.objects.filter(
                students=self.request.user).values('assignment') 
            topics = AssignedAssignment.objects.filter(
                students=self.request.user).values('assignment__topic')
            topics =Topic.objects.filter(pk__in=topics).annotate(total_assignments=Count(Case(
            When(assignments__in=required_assignments, then=1),output_field=IntegerField(),)))
            return topics


class GetTopicsForStudentViewV2(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = TopicNameSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        current = self.request.query_params.get("current")
        if current:
            if str(current).lower() == "true":
                context['current'] = True
            else:
                context['current'] = False
        return context

    def get_queryset(self):
        requesting_student = self.request.user
        return Topic.objects.filter(grade=requesting_student.clas.grade_level)

class GetAssignedAssignmentsStudentView(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = AssignmentNameSerializer

    def get_queryset(self):
        topic_id = self.kwargs.get('topic_id')
        get_object_or_not_found_exception(
            Topic, topic_id, "No Topic found with given id.")
        assignments = None
        student = self.request.user
        past_assignments = AssignedAssignment.objects.filter(from_date__lt=timezone.now(), to_date__lt=timezone.now(), assignment__topic=topic_id, students=student).values_list('assignment')
        submitted_assignments = AssignmentResult.objects.filter(student=student, assignment__topic=topic_id, ).values_list('assignment')
        current_assignments = AssignedAssignment.objects.filter(assignment__topic=topic_id, students=student).exclude(assignment__in=past_assignments).exclude(assignment__in=submitted_assignments).values_list('assignment')
        if 'current' in self.request.query_params:
            if str(self.request.query_params.get('current')).lower() == "true":
                assignments = Assignment.objects.filter(pk__in=current_assignments)
            else:
                assignments = Assignment.objects.filter(Q(pk__in=past_assignments) | Q(pk__in=submitted_assignments))
        else:
            assignments = AssignedAssignment.objects.filter(
                assignment__topic=topic_id, students=self.request.user).values('assignment')
            assignments = Assignment.objects.filter(pk__in= assignments)

        assignment_type = self.request.query_params.get('assignment_type')
        
        if assignment_type:
            assignments = assignments.filter(_type=assignment_type)
        return assignments


class GetAttemptedAssignmentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ShowResultDetailAssignmentSerializer
    lookup_field = 'assignment_id'

    def get_object(self):
        assignment_obj = get_object_or_not_found_exception(
            Assignment, self.kwargs.get('assignment_id'))
        if not AssignmentResult.objects.filter(student=self.request.user.pk, assignment=assignment_obj.pk).first():
            raise ValidationError("You have not submitted the assignment yet.")
        return assignment_obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['assignment_id'] = self.kwargs.get('assignment_id')
        return context


class GetStudentCompetencyReportView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = StudentCompetencyReportSerialzier

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        assignment_results = AssignmentResult.objects.filter(
            student=student_id)
        get_object_or_not_found_exception(Student, student_id)
        assignment_id = self.request.query_params.get('assignment_id')
        topic = self.request.query_params.get('topic')
        assignment_type = self.request.query_params.get('assignment_type')
        if assignment_id:
            assignment_results = assignment_results.filter(
                assignment=assignment_id)
        if topic:
            assignment_results = assignment_results.filter(
                assignment__topic=topic)

        if assignment_type:
            assignment_results = assignment_results.filter(
                assignment___type=assignment_type)

        return assignment_results.annotate(percentage=(F('marks_obtained')/F('total_marks'))*100)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # my code
        data = {'results': serializer.data}
        summary_results = queryset.aggregate(total_marks_obtained=Sum(
            'marks_obtained'), average_percentage=Avg('percentage'))
        data['summary'] = {'total_marks_obtained': summary_results['total_marks_obtained'],
                           'average_percentage': summary_results['average_percentage']}
        return Response(data)


class GetTeksDetailsReportView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeksDetailReportSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        class_id = self.kwargs.get('class_id')
        class_obj = get_object_or_not_found_exception(Class, class_id)
        assignments = Assignment.objects.filter(
            topic__grade=class_obj.grade_level)
        topic = self.request.query_params.get('topic')
        assignment_type = self.request.query_params.get('assignment_type')

        if topic:
            assignments = assignments.filter(topic=topic)

        if assignment_type:
            assignments = assignments.filter(_type=assignment_type)

        context['assignments'] = assignments
        return context

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        get_object_or_not_found_exception(Class, class_id)
        all_students_of_class = Student.objects.filter(clas=class_id)
        return all_students_of_class



class GetTeksDetailsReportViewV2(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = AssignmentDetailResultSerializer
    filterset_fields = ['topic','_type']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        class_id = self.kwargs.get('class_id')
        class_obj = get_object_or_not_found_exception(Class, class_id)
        get_object_or_not_found_exception(Class, class_id)
        all_students_of_class = Student.objects.filter(clas=class_id)

        context['all_students_of_class'] = all_students_of_class
        return context

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        class_obj = get_object_or_not_found_exception(Class, class_id)
        assignments = Assignment.objects.filter(
            topic__grade=class_obj.grade_level)
        return assignments

class GetStudentGrowthByTeksView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = GrowthByTeksReportSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['student_id'] = self.kwargs.get('student_id')
        return context

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        class_obj = get_object_or_not_found_exception(Class, class_id)
        return Topic.objects.filter(grade=class_obj.grade_level)


class GetAssignedAssignmentListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = AssignedAssignmentListSerializer

    filterset_fields = ['assignment']

    def get_queryset(self):
        class_id = self.kwargs.get('class_id')
        get_object_or_not_found_exception(Class, class_id)
        return AssignedAssignment.objects.get_all_assigned_assignment_of_class_with_counted_students(class_id)





class AssignedAssignmentRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_serializer_class(self):
        if self.request.method == "PATCH" or self.request.method == "DELETE":
            return AssignedAssignmentUpdateSerializer
        elif self.request.method == "GET":
            return AssignedAssignmentSerializer2

        raise MethodNotAllowed("The method you are trying is not allowed")

    def get_object(self):
        assigned_assignment_id = self.kwargs.get('assigned_assignment_id')
        return get_object_or_not_found_exception(AssignedAssignment, assigned_assignment_id)



class GetWorksheetView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorksheetDownloadSerializer

    def get_object(self):
        assignment_obj = get_object_or_not_found_exception(Assignment, self.kwargs.get('assignment_id'))
        if not assignment_obj._type == AssignmentTypeChoices.ASSESMENT_BY_WORKSHEET:
            raise ValidationError("given assingment is not of type assesment by worksheet")
        return assignment_obj

    

class GetAttemptedAssignmentViewV2(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmittedAssignmentSerializerVersion2
    queryset = Assignment.objects.all()


class GetTestQuestionView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = TestQuestion.objects.all()
    serializer_class = TestQuestionSerializer