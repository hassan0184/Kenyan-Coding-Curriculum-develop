from dataclasses import fields
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
import assignment
from common_utilities.utils import get_object_or_not_found_exception, get_pk_or_not_found_exception
from core.models import Class
from users.models import Student
from users.serializers import StudentNameSerializer
from assignment.models import (
    Assignment, AssignmentResult, FractionModel1,
    McqQuestion, McqOption, Topic,
    AssignedAssignment, AssignmentResultDetail,
    SortingQuestion, SortingQuestionOptions,
    FillInBlankQuestion, TextFieldForFillinBlankQuestion,
    OptionFieldForFillinBlankQuestion, CalculatorQuestion,
    DropDownQuestion, DropDownOption,
    TestQuestion, CalculatorQuestionAnswer
)

from .utils import assignment_is_submitted_before


class OptionSerializer(ModelSerializer):
    class Meta:
        model = McqOption
        fields = ['id', 'text', 'is_correct']


class ResultDetailOptionSerializer(ModelSerializer):
    was_marked_by_student = serializers.SerializerMethodField()

    def get_was_marked_by_student(self, option):
        assignment_result_detail_object = self.context.get(
            'assignment_result_detail_obj')
        if assignment_result_detail_object:
            return option in  assignment_result_detail_object.mcq_selected_options.all()
        return False

    class Meta:
        model = McqOption
        fields = ['id', 'text', 'is_correct', 'was_marked_by_student']


class QuestionSerializer(ModelSerializer):
    options = OptionSerializer(many=True)
    _type = serializers.SerializerMethodField()

    def get__type(self, obj):
        return "MCQ Question"
    class Meta:
        model = McqQuestion
        fields = ['id', 'title', 'options', '_type', 'max_select']


class ResultDetailQuestionSerializer(ModelSerializer):
    options = serializers.SerializerMethodField('get_options_serializer')
    obtained_marks = serializers.SerializerMethodField()

    def get_obtained_marks(self, question):
        assignment_result_object = AssignmentResultDetail.objects.filter(
            mcq_question=question, student=self.context.get('request').user.pk).first()
        if assignment_result_object is None:
            raise ValidationError("No result record found in db.")
        if assignment_result_object.mcq_selected_option.is_correct:
            return question.marks
        return 0


    def get_options_serializer(self, *args, **kwargs):
        question_obj = args[0]
        assignment_id = self.context.get('assignment_id')
        question_id = question_obj.pk
        student_id = self.context.get('request').user.pk
        assignment_result_detail_obj = AssignmentResultDetail.objects.filter(
            student=student_id, assignment=assignment_id, mcq_question=question_id).first()
        if not assignment_result_detail_obj:
            raise("Details for this assignments are not found in db.")
        serializer_context = {
            'assignment_result_detail_obj': assignment_result_detail_obj}
        all_options = question_obj.options.all()
        option_serializer = ResultDetailOptionSerializer(
            data=all_options, context=serializer_context, many=True)
        option_serializer.is_valid()
        return option_serializer.data

    class Meta:
        model = McqQuestion

        fields = ['id', 'title', 'obtained_marks', 'marks', 'options', ]


class ShowResultDetailAssignmentSerializer(ModelSerializer):
    questions = ResultDetailQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',
                  'questions', 'is_pre_test', 'is_post_test']


class AssignmentSerializer(ModelSerializer):
    questions = QuestionSerializer(many=True)
    name = serializers.CharField(source='get_assignment_complete_name')

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',
                  'questions', 'is_pre_test', 'is_post_test']


class AssignmentNameSerializer(ModelSerializer):
    name = serializers.CharField(source='get_assignment_complete_name')
    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',
                  'is_pre_test', 'is_post_test']


class TopicSerializer(ModelSerializer):
    assignments = AssignmentSerializer(many=True)
    class Meta:
        model = Topic
        fields = ['id', 'name', 'assignments']


class TopicNameSerializer(ModelSerializer):
    total_assignments = serializers.SerializerMethodField()
    
    def get_total_assignments(self, topic):
        total_assignments = topic.assignments.all().count()
        student = self.context.get("request").user
        if "current" in self.context:
            if self.context.get('current'):
                return topic.number_of_active_assignments(student)
            else:
                return topic.number_of_past_assignments(student)
        return topic.number_of_active_assignments(student) + topic.number_of_past_assignments(student)
    class Meta:
        model = Topic
        fields = ['id', 'name', 'total_assignments']


class AssignedAssignmentSerializer(ModelSerializer):

    from_date = serializers.DateTimeField(input_formats=[r"%m-%d-%Y",])
    to_date = serializers.DateTimeField(input_formats=[r"%m-%d-%Y",])
    class Meta:
        model = AssignedAssignment
        fields = ['assignment', 'students', 'from_date', 'to_date', '_class']

    def validate(self, attrs):
        if attrs['from_date'].date() >= attrs['to_date'].date():
            raise ValidationError(
                'starting date should be of before ending date.')

        if AssignedAssignment.objects.filter(assignment=attrs['assignment'].pk, students__in=attrs['students']):
            raise ValidationError(
                "You cannot add assign assignment to a student again.")

        if self.context.get("assign_to_entire_class"):
            attrs['students'] = Class.objects.get(
                pk=attrs['_class'].pk).students.all()
            if AssignedAssignment.objects.filter(assignment=attrs['assignment'], students__in=attrs['students']):
                raise ValidationError(
                    "You cannot assign assignment to whole class assignment is assiged to some students before.")
        else:
            student_ids = []
            for student in attrs['students']:
                student_ids.append(student.pk)
            attrs['students'] = Student.objects.filter(pk__in=student_ids)
        return attrs

    def create(self, validated_data):
        assigned_assignment_obj = AssignedAssignment(
            assignment=validated_data['assignment'], _class=validated_data['_class'], from_date=validated_data['from_date'], to_date=validated_data['to_date'])
        assigned_assignment_obj.save()
        assigned_assignment_obj.students.add(*validated_data['students'])
        assigned_assignment_obj.save()
        return assigned_assignment_obj


class AssignmentResultDetailSerializer(ModelSerializer):
    class Meta:
        model = AssignmentResultDetail
        fields = '__all__'

    def validate(self, attrs):
        assignment_is_submitted_before(self.context.get(
            'student_id'), self.context.get('assignment_id'))
        # assignment_have_given_question_or_bad_request(
        #     self.context.get('assignment_id'), attrs['question'].pk)
        # if attrs['selected_option']:
        #     question_have_given_option_or_bad_request(
        #         attrs['question'].pk, attrs['selected_option'].pk)
        return super().validate(attrs)


class StudentCompetencyReportSerialzier(serializers.ModelSerializer):
    percentage = serializers.DecimalField(4, 2)
    assignment = serializers.CharField(source='assignment.name')

    class Meta:
        model = AssignmentResult
        fields = ['id', 'assignment', 'marks_obtained',
                  'total_marks', 'percentage']


class ResultSerializer(serializers.ModelSerializer):
    marks_obtained = serializers.SerializerMethodField()

    def get_marks_obtained(self, assignment):
        result = AssignmentResult.objects.filter(
            assignment=assignment.pk, student=self.context.get('student').pk).first()
        if result:
            return result.marks_obtained
        return 0

    class Meta:
        model = Assignment
        fields = ['name', 'marks_obtained']


class TeksDetailReportSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        assignments = self.context.get('assignments')
        result_serializer = ResultSerializer(
            data=assignments, many=True, context={'student': obj})
        result_serializer.is_valid()
        return result_serializer.data

    class Meta:
        model = Student
        fields = ["username", "results"]


class StudentResultSerializer(serializers.ModelSerializer):
    marks_obtained = serializers.SerializerMethodField()

    def get_marks_obtained(self,student):
        assignment = self.context.get('assignment')
        result = AssignmentResult.objects.filter(
            assignment=assignment.pk, student=student.pk).first()
        if result:
            return result.marks_obtained
        return 0
        
    class Meta:
        model = Student
        fields = ['id', 'username','marks_obtained']


class AssignmentDetailResultSerializer(serializers.ModelSerializer):

    results = serializers.SerializerMethodField()
    
    def get_results(self,assignment):
        all_students_of_class = self.context.get("all_students_of_class")
        student_result_serializer = StudentResultSerializer(data=all_students_of_class,many=True,context={'assignment':assignment})
        student_result_serializer.is_valid()
        return student_result_serializer.data

    class Meta:
        model = Assignment
        fields = ['id','name','results']




class GrowthByTeksReportSerializer(serializers.ModelSerializer):

    pre_test_marks = serializers.SerializerMethodField()
    post_test_marks = serializers.SerializerMethodField()

    def get_pre_test_marks(self, topic):
        assignment_result_obj = AssignmentResult.objects.filter(
            assignment__topic=topic, assignment__is_pre_test=True, student=self.context.get('student_id')).first()
        if assignment_result_obj:
            return assignment_result_obj.marks_obtained
        return 0

    def get_post_test_marks(self, topic):
        assignment_result_obj = AssignmentResult.objects.filter(
            assignment__topic=topic, assignment__is_post_test=True, student=self.context.get('student_id')).first()
        if assignment_result_obj:
            return assignment_result_obj.marks_obtained
        return 0

    class Meta:
        model = Topic
        fields = ['name', 'pre_test_marks', 'post_test_marks']


class AssignedAssignmentListSerializer(serializers.ModelSerializer):
    no_of_students = serializers.CharField()
    assignment_name = serializers.CharField(source='assignment.name')

    class Meta:
        model = AssignedAssignment
        fields = ['id','assignment','assignment_name' ,'from_date',
                  'to_date', '_class', 'no_of_students']


class AssignedAssignmentSerializer2(serializers.ModelSerializer):
    students = StudentNameSerializer(many=True)
    assignment = serializers.CharField(source='assignment.name')

    class Meta:
        model = AssignedAssignment
        fields = ['id', 'assignment', 'from_date',
                  'to_date', '_class', 'students']


class AssignedAssignmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignedAssignment
        fields = ['id', 'assignment', 'from_date',
                  'to_date', '_class', 'students']



class WorksheetDownloadSerializer(serializers.ModelSerializer):
    worksheet = serializers.SerializerMethodField()

    def get_worksheet(self,obj):
        return self.context['request'].build_absolute_uri(obj.worksheet.url)

    class Meta:
        model = Assignment
        fields = ['id','worksheet']






class SortingQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortingQuestionOptions
        fields = ['id','text','correct_sorting_number']

class SortingQuestionSerializer(serializers.ModelSerializer):
    options = SortingQuestionOptionSerializer(many=True)
    _type = serializers.SerializerMethodField()

    def get__type(self, obj):
        return "Sorting Question"
    class Meta:
        model = SortingQuestion
        fields = [ "id","text","options","_type"]



class OptionFieldForFillinBlankQuestionSerializer(ModelSerializer):
    class Meta:
        model = OptionFieldForFillinBlankQuestion
        fields = ["id","text","is_correct"]



class TextFieldForFillinBlankQuestionSerializer(ModelSerializer):
    options = OptionFieldForFillinBlankQuestionSerializer(many=True)
    class Meta:
        model = TextFieldForFillinBlankQuestion
        fields = ["id", "question","text","options"]



class FillInBlankQuestionSerializer(ModelSerializer):
    text_fields = TextFieldForFillinBlankQuestionSerializer(many=True)
    _type = serializers.SerializerMethodField()

    def get__type(self, obj):
        return "Fill in the blank Question"
    class Meta:
        model = FillInBlankQuestion
        fields = ["id", "text_fields", "_type"]

class CalculatorQuestionAnswerSerializer(ModelSerializer):
    class Meta:
        model = CalculatorQuestionAnswer
        fields = "__all__"


class CalculatorQuestionSerializer(ModelSerializer):
    _type = serializers.SerializerMethodField()
    
    def get__type(self, obj):
        return "Calculator Question"

    class Meta:
        model = CalculatorQuestion
        fields = ['id','text','_type']


class DropDownOptionSerializer(ModelSerializer):
    class Meta:
        model = DropDownOption
        fields = ["id","text","is_correct"]


class DropDownQuestionSerializer(ModelSerializer):
    options = DropDownOptionSerializer(many=True)
    _type = serializers.SerializerMethodField()

    def get__type(self, obj):
        return "Drop Down Question"
    class Meta:
        model = DropDownQuestion
        fields = ["id", "assignment","text","options","_type"]


class AssignmentSerializer2(ModelSerializer):
    questions = QuestionSerializer(many=True)
    name = serializers.CharField(source='get_assignment_complete_name')
    sorting_questions = SortingQuestionSerializer(many=True)
    fill_in_blank_questions = FillInBlankQuestionSerializer(many=True)
    calculator_questions = CalculatorQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',
                  'questions', 'is_pre_test', 
                  'is_post_test',"sorting_questions",
                  "fill_in_blank_questions",
                  "calculator_questions"]


class AssignmentSerializer2(ModelSerializer):
    questions = QuestionSerializer(many=True)
    name = serializers.CharField(source='get_assignment_complete_name')
    sorting_questions = SortingQuestionSerializer(many=True)
    fill_in_blank_questions = FillInBlankQuestionSerializer(many=True)
    calculator_questions = CalculatorQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',
                  'questions', 'is_pre_test', 
                  'is_post_test',"sorting_questions",
                  "fill_in_blank_questions",
                  "calculator_questions"]




def add_serializer_data_to_list(serializer,_list):
    serializer.is_valid()
    _list.extend(serializer.data)

class AssignmentSerializerVersion2(ModelSerializer):
    name = serializers.CharField(source='get_assignment_complete_name')
    each_question_marks = serializers.SerializerMethodField()
    all_questions = serializers.SerializerMethodField()

    def get_each_question_marks(self, assignment):
        return "{:.2f}".format(assignment.get_each_question_marks_in_assignment())

    def get_all_questions(self,assignment):
        data = []
        question_serializer = QuestionSerializer(data=assignment.questions.all(),many=True)
        add_serializer_data_to_list(question_serializer, data)
        sorting_question_serializer = SortingQuestionSerializer(data=assignment.sorting_questions.all(), many=True)
        add_serializer_data_to_list(sorting_question_serializer, data)
        fill_in_blank_question_serializer = FillInBlankQuestionSerializer(data=assignment.fill_in_blank_questions.all(),many=True)
        add_serializer_data_to_list(fill_in_blank_question_serializer, data)
        # calculator_question_serializer = CalculatorQuestionSerializer(data=assignment.calculator_questions.all(), many=True)
        # add_serializer_data_to_list(calculator_question_serializer, data)
        # drop_down_question_serializer = DropDownQuestionSerializer(data=assignment.dropdown_questions.all(),many=True)
        # add_serializer_data_to_list(drop_down_question_serializer, data)
        fraction_model1_question_serializer = FractionModel1Serializer(data=assignment.fraction_model1_questions.all(), many=True)
        add_serializer_data_to_list(fraction_model1_question_serializer, data)
        return data

    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',"each_question_marks",
                  'all_questions', 'is_pre_test']

class SortingQuestionOptionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortingQuestionOptions
        fields = ['id','text','correct_sorting_number']


class SortingQuestionResultSerializer(serializers.ModelSerializer):
    options = SortingQuestionOptionResultSerializer(many=True)
    _type = serializers.SerializerMethodField()
    obtained_marks = serializers.SerializerMethodField()
    marks = serializers.SerializerMethodField()

    def get_marks(self, sorting_question):
        return sorting_question.assignment.get_each_question_marks_in_assignment()

    def get_obtained_marks(self, sorting_question):
        assignment_result_detail_object = AssignmentResultDetail.objects.filter(
            sorting_question=sorting_question, student=self.context.get('request').user.pk).first()
        if assignment_result_detail_object is None:
            return 0
        return sorting_question.get_obtained_marks(assignment_result_detail_object.sorting_question_selected_options.all())

    def get__type(self, obj):
        return "Sorting Question"

    class Meta:
        model = SortingQuestion
        fields = [ "id","text","marks","obtained_marks","options","_type"]



class OptionFieldForFillinBlankQuestionResultSerializer(ModelSerializer):
    was_marked_by_student = serializers.SerializerMethodField()

    def get_was_marked_by_student(self, option):
        assignment_result_detail_object = self.context.get(
            'assignment_result_detail_obj')
        if assignment_result_detail_object:
            return option in  assignment_result_detail_object.fill_in_the_blank_question_answers.all()
        return False

    class Meta:
        model = OptionFieldForFillinBlankQuestion
        fields = ["id","text","is_correct","was_marked_by_student"]


class TextFieldForFillinBlankQuestionResultSerializer(ModelSerializer):
    options = serializers.SerializerMethodField()

    def get_options(self, text_field_obj):
        serializer = OptionFieldForFillinBlankQuestionResultSerializer(data=text_field_obj.options.all(),many=True,context=self.context)
        serializer.is_valid()
        return serializer.data
        



    class Meta:
        model = TextFieldForFillinBlankQuestion
        fields = ["id", "question","text","options"]


class FillInBlankQuestionResultSerializer(ModelSerializer):
    text_fields = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()
    obtained_marks = serializers.SerializerMethodField()
    marks = serializers.SerializerMethodField()
    
    def get_marks(self, fill_blank_question):
        return fill_blank_question.assignment.get_each_question_marks_in_assignment()

    def get_text_fields(self, question):
        user = self.context.get('request').user
        assignment = self.context.get("assignment")
        assignment_result_detail_obj =  AssignmentResultDetail.objects.filter(assignment=assignment,student=user,fill_in_the_blank_question = question).first()
        self.context['assignment_result_detail_obj'] = assignment_result_detail_obj
        serializer = TextFieldForFillinBlankQuestionResultSerializer(data=question.text_fields.all(),many=True,context=self.context)
        serializer.is_valid()
        return serializer.data

    def get_obtained_marks(self, fill_in_blank_question):
        assignment_result_detail_object = AssignmentResultDetail.objects.filter(
            fill_in_the_blank_question=fill_in_blank_question, student=self.context.get('request').user.pk).first()
        if assignment_result_detail_object is None:
            return 0
        return fill_in_blank_question.get_obtained_marks(assignment_result_detail_object.fill_in_the_blank_question_answers.all())

    def get__type(self, obj):
        return "Fill in the blank Question"

    class Meta:
        model = FillInBlankQuestion
        fields = ["id", "text_fields", "_type","marks",'obtained_marks']


class DropDownOptionResultSerializer(ModelSerializer):
    was_marked_by_student = serializers.SerializerMethodField()

    def get_was_marked_by_student(self, option):
        assignment_result_detail_object = self.context.get(
            'assignment_result_detail_obj')
        return assignment_result_detail_object.drop_down_selected_option == option

    class Meta:
        model = DropDownOption
        fields = ["id","text","is_correct","was_marked_by_student"]


class DropDownQuestionResultSerializer(ModelSerializer):
    options = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()
    obtained_marks = serializers.SerializerMethodField()


    def get_obtained_marks(self, question):
        assignment_result_object = AssignmentResultDetail.objects.filter(
            drop_down_question=question, student=self.context.get('request').user.pk).first()
        if assignment_result_object is None:
            raise ValidationError("No result record found in db.")
        if assignment_result_object.drop_down_selected_option.is_correct:
            return question.marks
        return assignment_result_object.marks


    def get_options(self, drop_down_question_obj):
        user = self.context.get('request').user
        assignment = self.context.get("assignment")
        assignment_result_detail_obj =  AssignmentResultDetail.objects.filter(assignment=assignment,student=user,drop_down_question= drop_down_question_obj).first()
        self.context['assignment_result_detail_obj'] = assignment_result_detail_obj
        serializer = DropDownOptionResultSerializer(data=drop_down_question_obj.options.all(),many=True,context=self.context)
        serializer.is_valid()
        return serializer.data

    def get__type(self, obj):
        return "Drop Down Question"
    class Meta:
        model = DropDownQuestion
        fields = ["id", "assignment" ,"marks","obtained_marks","text","options","_type"]


class CalculatorQuestionResultSerializer(ModelSerializer):
    _type = serializers.SerializerMethodField()
    given_answer = serializers.SerializerMethodField()

    obtained_marks = serializers.SerializerMethodField()


    def get_obtained_marks(self, question):
        assignment_result_object = AssignmentResultDetail.objects.filter(
            calculator_question=question, student=self.context.get('request').user.pk).first()
        if assignment_result_object is None:
            raise ValidationError("No result record found in db.")
        return assignment_result_object.marks


    def get_given_answer(self, calculator_question_obj):
        user = self.context.get("request").user
        assignment = self.context.get("assignment")
        assignment_result_detail_obj = AssignmentResultDetail.objects.get(student=user, assignment=assignment, calculator_question=calculator_question_obj)
        return assignment_result_detail_obj.calculator_question_answer

    def get__type(self, obj):
        return "Calculator Question"

    class Meta:
        model = CalculatorQuestion
        fields = ['id','text','answer','given_answer','marks','obtained_marks','_type']


class FractionModel1Serializer(ModelSerializer):
    _type = serializers.SerializerMethodField()
    total_boxes_array = serializers.SerializerMethodField()

    def get_total_boxes_array(self, fraction_model_1):
        return [" " for _ in range(fraction_model_1.total_boxes)]

    def get__type(self, obj):
        return "Fraction model 1"

    class Meta:
        model = FractionModel1
        fields = ['id', 'text', "total_boxes","total_boxes_array", "correct_number", "_type"]


class QuestionResultSerializerV2(ModelSerializer):
    options = serializers.SerializerMethodField()
    marks = serializers.SerializerMethodField()
    _type = serializers.SerializerMethodField()
    obtained_marks = serializers.SerializerMethodField()

    def get_marks(slef, question):
        return question.assignment.get_each_question_marks_in_assignment()

    def get_options(self,question):
        context = self.context
        user = self.context.get('request').user
        context['assignment_result_detail_obj'] = AssignmentResultDetail.objects.filter(student=user, assignment=self.context.get('assignment'), mcq_question=question).first()
        options = ResultDetailOptionSerializer(data=question.options.all(), many=True, context=context) 
        options.is_valid()
        return options.data

    def get_obtained_marks(self, question):

        assignment_result_object = AssignmentResultDetail.objects.filter(
            mcq_question=question, student=self.context.get('request').user.pk).first()
        if assignment_result_object is None:
            return 0
        return assignment_result_object.mcq_question.get_obtained_marks(assignment_result_object.mcq_selected_options.all())


    def get__type(self, obj):
        return "MCQ Question"

    class Meta:
        model = McqQuestion
        fields = ['id', 'title', 'options', '_type','marks', 'obtained_marks']


class SubmittedAssignmentSerializerVersion2(ModelSerializer):
    name = serializers.CharField(source='get_assignment_complete_name')
    all_questions = serializers.SerializerMethodField()

    def get_all_questions(self,assignment):
        data = []
        context = self.context
        context['assignment'] = assignment
        
        question_serializer = QuestionResultSerializerV2(data=assignment.questions.all(),many=True,context=context)
        add_serializer_data_to_list(question_serializer, data)
        
        sorting_question_serializer = SortingQuestionResultSerializer(data=assignment.sorting_questions.all(), many=True,context=context)
        add_serializer_data_to_list(sorting_question_serializer, data)
        
        fill_in_blank_question_serializer = FillInBlankQuestionResultSerializer(data=assignment.fill_in_blank_questions.all(),many=True,context=context)
        add_serializer_data_to_list(fill_in_blank_question_serializer, data)

        fraction_model1_question_serializer = FractionModel1ResultSerializer(data=assignment.fraction_model1_questions.all(),many=True,context=context)
        add_serializer_data_to_list(fraction_model1_question_serializer, data)
        
        # calculator_question_serializer = CalculatorQuestionResultSerializer(data=assignment.calculator_questions.all(), many=True, context=context)
        # add_serializer_data_to_list(calculator_question_serializer, data)

        # drop_down_question_serializer = DropDownQuestionResultSerializer(data=assignment.dropdown_questions.all(),many=True, context=context)
        # add_serializer_data_to_list(drop_down_question_serializer, data)

        return data



    class Meta:
        model = Assignment
        fields = ['id', 'name', 'topic', '_type',
                  'all_questions', 'is_pre_test']




class TestQuestionSerializer(ModelSerializer):
    class Meta:
        model = TestQuestion
        fields = "__all__"


class FractionModel1ResultSerializer(ModelSerializer):
    marked_indexes = serializers.SerializerMethodField()
    marks = serializers.SerializerMethodField()
    obtained_marks = serializers.SerializerMethodField()

    def get_marked_indexes(self, fraction_model1_question):
        student = self.context.get("request").user
        result_detail_obj = AssignmentResultDetail.objects.filter(student=student, assignment=self.context.get("assignment"),fraction_model_1_question=fraction_model1_question).first()
        if result_detail_obj:
            return result_detail_obj.fraction_model_1_answers.split(",")
        return []

    def get_marks(self, fraction_model1_question):
        return fraction_model1_question.assignment.get_each_question_marks_in_assignment()

    def get_obtained_marks(self, fraction_model1_question):
        student = self.context.get("request").user
        result_detail_obj = AssignmentResultDetail.objects.filter(student=student, assignment=self.context.get("assignment"),fraction_model_1_question=fraction_model1_question).first()
        if result_detail_obj:
            return result_detail_obj.fraction_model_1_question.get_obtained_marks(result_detail_obj.fraction_model_1_answers)
        return []

    class Meta:
        model = FractionModel1
        fields = ['text',"total_boxes","correct_number","marked_indexes","marks","obtained_marks"]

