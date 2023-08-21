from django.db.models import Case, When
from django.db import models
from users.models import Student
from core.models import Class
from common_utilities.choices import GradeLevelChoices, AssignmentTypeChoices
from users.models import Student
from common_utilities.utils import get_object_or_not_found_exception
from core.models import Class, Grade
from django.utils import timezone
from django.db.models import Count
from .validators import validate_pdf
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField 
from common_utilities.ck_editor_configs import CK_CONFIG_FOR_MCQ_OPTIONS


class Topic(models.Model):
    name = models.CharField(max_length=255)
    grade = models.ForeignKey(to=Grade, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.name} (grade {self.grade} )'


    def number_of_active_assignments(self, student):
        submitted_assignments = AssignmentResult.objects.filter(student=student, assignment__topic=self).values_list('assignment').count()
        all_assignments = Assignment.objects.filter(topic=self)
        current_assignments = AssignedAssignment.objects.filter(from_date__lte=timezone.now(), to_date__gte=timezone.now(), assignment__topic=self, students=student).exclude(assignment___type=3).values_list('assignment').count()
        return current_assignments  - submitted_assignments


    def number_of_past_assignments(self, student):
        submitted_assignments = AssignmentResult.objects.filter(student=student, assignment__topic=self).values_list('assignment').count()
        past_assignments =  AssignedAssignment.objects.filter(from_date__lt=timezone.now(), to_date__lt=timezone.now(), assignment__topic=self, students=student).exclude(assignment___type=3).values_list('assignment').count()
        return past_assignments + submitted_assignments

    class Meta:
        unique_together = ('name', 'grade')


class AssignmentManager(models.Manager):
    def get_all_assignments_of_class(self, class_id: int):
        class_obj = get_object_or_not_found_exception(Class, class_id)
        return self.filter(topic__grade=class_obj.grade_level)


class Assignment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    topic = models.ForeignKey(
        to=Topic, on_delete=models.CASCADE, related_name="assignments")
    _type = models.CharField(
        max_length=30,
        choices=AssignmentTypeChoices.choices,
        default=AssignmentTypeChoices.ASSESMENT_BY_TEKS)
    is_pre_test = models.BooleanField(default=False)
    is_post_test = models.BooleanField(default=False)
    worksheet = models.FileField(upload_to='worksheets/',null=True,blank=True,validators=[validate_pdf])
    marks = models.IntegerField(default=100)
    objects = AssignmentManager()

    def get_total_no_of_questions(self):
        total_questions = 0
        total_questions += self.questions.all().count() # this is for counting mcq questions
        total_questions += self.fraction_model1_questions.all().count()
        total_questions += self.fill_in_blank_questions.all().count()
        total_questions += self.sorting_questions.all().count()
        total_questions += self.calculator_questions.all().count()
        return total_questions

    def get_each_question_marks_in_assignment(self):
        """returns the marks of that question in the assignment"""
        return self.marks / self.get_total_no_of_questions()

    def get_marks(self):
        return self.marks

    def clean(self) -> None:
        if self._type == AssignmentTypeChoices.ASSESMENT_BY_WORKSHEET and self.worksheet.name is None:
            raise ValidationError("You have to upload the worksheet if the assignment type is Assesment by Worksheet.")
        
        if self.worksheet.name and  not self._type == AssignmentTypeChoices.ASSESMENT_BY_WORKSHEET:
            raise ValidationError("You can only upload worksheet if the assignment type is assesment by worksheet.")
    

    def get_assignment_complete_name(self):
        addon = ""
        if self.is_pre_test:
            addon = "(pre test)"
        elif self.is_post_test:
            addon = "(post test)"
        return f"{self.name} {addon}"

    def __str__(self) -> str:
        return self.name


class McqQuestion(models.Model):
    title = RichTextUploadingField()
    assignment = models.ForeignKey(
        to=Assignment, on_delete=models.CASCADE, related_name='questions')
    max_select = models.IntegerField(default=1)

    def __str__(self) -> str:
        return self.title

    def get_partial_marks(self):
        return self.assignment.get_each_question_marks_in_assignment() / self.max_select


    def get_obtained_marks(self, mcq_selected_options):
        marks_obtained = 0
        
        if (self.max_select < mcq_selected_options.count()):
            raise ValidationError(f"the question with id {self.id} only allows to be  {self.max_select} options selected as max.")

        for selected_option in mcq_selected_options:
            if selected_option.is_correct:
                marks_obtained += self.get_partial_marks()

        return marks_obtained


class McqOption(models.Model):
    text = RichTextUploadingField()
    question = models.ForeignKey(
        to=McqQuestion, on_delete=models.CASCADE, related_name='options')
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.text


class AssignmentResult(models.Model):
    assignment = models.ForeignKey(
        to=Assignment, on_delete=models.CASCADE, related_name='result')
    student = models.ForeignKey(
        to=Student, on_delete=models.CASCADE, related_name='result')
    marks_obtained = models.DecimalField(decimal_places=2, max_digits=7)

    def __str__(self) -> str:
        return f"{self.assignment} -- {self.student} -- {self.marks_obtained}"


class AssignedAssignmentManager(models.Manager):
    def get_all_students_of_a_class_wrt_assignment(self, teacher,  class_, assignment):
        """
        this function will give all the students of a particular class wrt assignent with a
        variable is_assigned means if the assignment is assigned or not
        """
        assigned_assignment_objs = self.filter(assignment=assignment, _class=class_)
        students_with_assignment_assigned = []
        if assigned_assignment_objs:
            for assigned_assignment_obj in assigned_assignment_objs:
                students_with_assignment_assigned.extend(assigned_assignment_obj.students.all().values_list('pk',flat=True))

        return teacher.classes.get(pk=class_).students.all().annotate(
            is_assigned=Case(
                When(pk__in=students_with_assignment_assigned, then=True), default=False)
        )

    def get_all_assigned_assignment_of_class(self, class_id):
        '''
        this method will return all the assigned assignment objects that are assigned to a given class
        '''
        class_obj = get_object_or_not_found_exception(Class, class_id)
        return self.filter(_class=class_id, assignment__in=Assignment.objects.get_all_assignments_of_class(class_id))

    def get_all_assigned_assignment_of_student(self,class_id ,student_id):
        '''
        this method will return all the assigned assignment objects that are assigned to a given class
        '''
        return self.filter(_class = class_id,  students=student_id)

    def get_all_in_progress_assignments_of_class(self, class_id, student_id=None):
        if not student_id:
            return Assignment.objects.filter(pk__in=self.get_all_assigned_assignment_of_class(class_id).filter(from_date__lte=timezone.now(), to_date__gt=timezone.now()).values_list('assignment'))
        return Assignment.objects.filter(pk__in=self.get_all_assigned_assignment_of_student(class_id,student_id).filter(from_date__lte=timezone.now(), to_date__gt=timezone.now()).values_list('assignment'))


    def get_all_completed_assignments_of_class(self, class_id, student_id=None):
        if not student_id:
            return Assignment.objects.filter(pk__in=self.get_all_assigned_assignment_of_class(class_id).filter(from_date__lte=timezone.now(), to_date__lte=timezone.now()).values_list('assignment'))

        return Assignment.objects.filter(pk__in=AssignmentResult.objects.filter(student=student_id).values('assignment'))
        # return Assignment.objects.filter(pk__in=self.get_all_assigned_assignment_of_student(class_id ,student_id).filter(from_date__lte=timezone.now(), to_date__lte=timezone.now()).values_list('assignment'))

    def get_all_not_started_assignments_of_class(self, class_id, student_id=None):
        if not student_id:
            return Assignment.objects.filter(pk__in=self.get_all_assigned_assignment_of_class(class_id).filter(from_date__gt=timezone.now(), to_date__gt=timezone.now()).values_list('assignment'))
        return Assignment.objects.filter(pk__in=self.get_all_assigned_assignment_of_student(class_id,student_id).filter(from_date__gt=timezone.now(), to_date__gt=timezone.now()).values_list('assignment'))

    def get_all_assigned_assignment_of_class_with_counted_students(self, class_id):
        return self.filter(_class=class_id).annotate(no_of_students=Count('students'))


class AssignedAssignment(models.Model):
    assignment = models.ForeignKey(
        to=Assignment, on_delete=models.CASCADE, related_name="assigned_assignments")
    _class = models.ForeignKey(
        to=Class, on_delete=models.CASCADE, related_name="assigned_assignments")
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    students = models.ManyToManyField(
        to=Student)

    objects = AssignedAssignmentManager()

    def __str__(self) -> str:
        return f"{self.assignment} {self.students}"


class FillInBlankQuestion(models.Model):
    assignment = models.ForeignKey("assignment",on_delete=models.CASCADE, related_name="fill_in_blank_questions")
    
    def get_partial_marks(self):
        number_of_parts = OptionFieldForFillinBlankQuestion.objects.filter(question__question=self.pk).values('question').annotate(nums=Count("question")).filter(nums__gt=0).count()
        return self.assignment.get_each_question_marks_in_assignment() / number_of_parts

    def get_obtained_marks(self, answers):
        """ answers will be the list of  OptionFieldForFillinBlankQuestion"""
        number_of_corrections = 0
        for answer in answers:
            if answer.is_correct:
                number_of_corrections += 1
        return number_of_corrections * self.get_partial_marks()


class TextFieldForFillinBlankQuestion(models.Model):
    question = models.ForeignKey(to="FillInBlankQuestion",on_delete=models.CASCADE, related_name="text_fields")
    text = RichTextUploadingField()
    sorting_number = models.PositiveIntegerField()


class OptionFieldForFillinBlankQuestion(models.Model):
    question = models.ForeignKey(to="TextFieldForFillinBlankQuestion", on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=250)
    is_correct = models.BooleanField(default=False) 


class SortingQuestion(models.Model):
    assignment = models.ForeignKey(to="Assignment",on_delete=models.CASCADE, related_name="sorting_questions")
    text = RichTextUploadingField()

    def get_obtained_marks(self,answer):
        """ answer is going to be a lis of all marked Sorting question options """
        actual_options = self.options.all().order_by("correct_sorting_number").values('id') 
        selected_options = answer.all().values('id')
        try:
            for i in range(len(actual_options)):
                if not (actual_options[i] == selected_options[i]):
                    return 0
        except Exception as e:
            return 0
        return self.assignment.get_each_question_marks_in_assignment()



class SortingQuestionOptions(models.Model):
    question = models.ForeignKey(to="SortingQuestion", on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=300)
    correct_sorting_number = models.PositiveIntegerField(default=1) 


class CalculatorQuestion(models.Model):
    assignment = models.ForeignKey(to="Assignment",on_delete=models.CASCADE, related_name="calculator_questions")
    text = RichTextUploadingField()


class CalculatorQuestionAnswer(models.Model):
    calculator_question = models.ForeignKey(to="CalculatorQuestion", on_delete=models.CASCADE, related_name="possible_answers")
    answer = RichTextUploadingField()
    

class DropDownQuestion(models.Model):
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    assignment = models.ForeignKey(to="Assignment",on_delete=models.CASCADE, related_name="dropdown_questions")
    text = RichTextUploadingField()


class DropDownOption(models.Model):
    dropdown_question = models.ForeignKey(to="DropDownQuestion",on_delete=models.CASCADE,related_name="options")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(verbose_name='is correct',default=False)


class AssignmentResultDetail(models.Model):
    assignment = models.ForeignKey(to=Assignment, on_delete=models.CASCADE, related_name='result_details')
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE, related_name='result_details')
    mcq_question = models.ForeignKey(to=McqQuestion, on_delete=models.CASCADE, related_name='results', null=True, blank=True, default=None)
    mcq_selected_options = models.ManyToManyField(to=McqOption, related_name="selected_options", blank=True)
    calculator_question = models.ForeignKey(to=CalculatorQuestion, on_delete=models.CASCADE, related_name="results", null=True, blank=True, default=None)
    calculator_question_answer = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    drop_down_question = models.ForeignKey(to=DropDownQuestion, on_delete=models.CASCADE, related_name="results", null=True, blank=True, default=None)
    drop_down_selected_option = models.ForeignKey(to=DropDownOption, on_delete=models.CASCADE, related_name='results', null=True, blank=True, default=None)
    sorting_question = models.ForeignKey(to=SortingQuestion, on_delete=models.CASCADE, related_name="results", null=True, blank=True, default=None)
    sorting_question_selected_options = models.ManyToManyField(to=SortingQuestionOptions, related_name="results", blank=True)
    fill_in_the_blank_question = models.ForeignKey(to=FillInBlankQuestion, on_delete=models.CASCADE, related_name="results", null=True, blank=True, default=None)
    fill_in_the_blank_question_answers = models.ManyToManyField(to=OptionFieldForFillinBlankQuestion, related_name="results", blank=True)
    fraction_model_1_question = models.ForeignKey(to="FractionModel1", on_delete=models.CASCADE, related_name="results", blank=True, null=True, default=True)
    fraction_model_1_answers = models.CharField(max_length=1000, blank=True, null=True, default=True)


class TestQuestion(models.Model):
    assignment = models.ForeignKey(to=Assignment, on_delete=models.CASCADE, related_name="testing_questions")
    text = RichTextUploadingField()  # for uploading the file


class FractionModel1(models.Model):
    assignment = models.ForeignKey(to=Assignment, on_delete=models.CASCADE, related_name="fraction_model1_questions")
    text = RichTextUploadingField()
    total_boxes = models.IntegerField()
    correct_number = models.IntegerField()

    def get_obtained_marks(self, answers: str):
        obtained_marks = 0
        if len(answers.split(',')) == self.correct_number:
            obtained_marks = self.assignment.get_each_question_marks_in_assignment()
        return obtained_marks