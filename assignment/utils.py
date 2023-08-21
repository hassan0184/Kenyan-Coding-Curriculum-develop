from django.db.models import Count
from rest_framework.exceptions import ValidationError
from .models import AssignedAssignment, Assignment, AssignmentResult, McqQuestion, AssignmentResultDetail, OptionFieldForFillinBlankQuestion
from users.models import Student
from rest_framework.exceptions import NotFound
from common_utilities.utils import get_object_or_bad_request_exception



def get_completed_in_progress_not_started_assignments_of_class(class_id):
    all_complted_assignments_of_class = AssignedAssignment.objects.get_all_completed_assignments_of_class(
        class_id)
    all_in_progress_assignments_of_class = AssignedAssignment.objects.get_all_in_progress_assignments_of_class(
        class_id)
    all_not_started_assignments_of_class = AssignedAssignment.objects.get_all_not_started_assignments_of_class(
        class_id)
    return (all_complted_assignments_of_class, all_in_progress_assignments_of_class, all_not_started_assignments_of_class)


def get_completed_in_progress_not_started_assignments_of_student(student_id):
    class_id = Student.objects.get(pk=student_id).id
    all_complted_assignments_of_class = AssignedAssignment.objects.get_all_completed_assignments_of_class(
        class_id, student_id)
    all_in_progress_assignments_of_class = AssignedAssignment.objects.get_all_in_progress_assignments_of_class(
        class_id, student_id)
    all_not_started_assignments_of_class = AssignedAssignment.objects.get_all_not_started_assignments_of_class(
        class_id, student_id)
    return (all_complted_assignments_of_class, all_in_progress_assignments_of_class, all_not_started_assignments_of_class)


def assignment_have_given_question_or_bad_request(assignment_id, question_id):
    assignment_obj = get_object_or_bad_request_exception(
        Assignment, assignment_id)
    if not assignment_obj.questions.filter(pk=question_id).first():
        return NotFound(f"No Question is there with id {question_id} in assignment {assignment_obj.name}")


def assignment_is_submitted_before(student_id, assignment_id):
    if AssignmentResult.objects.filter(student=student_id, assignment=assignment_id):
        raise ValidationError("You have submitted this assignment before.")


def question_have_given_option_or_bad_request(question_id, option_id):
    question_obj = get_object_or_bad_request_exception(McqQuestion, question_id)
    if not question_obj.options.filter(pk=option_id).first():
        raise NotFound(
            f"No Question is there with id {option_id} in assignment {question_obj.title}")


def create_assignment_result_from_assignment_result_details(assignment_id, student):
    total_marks = 0
    marks_obtained = 0
    assignment = Assignment.objects.get(pk=assignment_id)
    assignment_result_details = AssignmentResultDetail.objects.filter(assignment=assignment_id, student=student.id)
    result_detail_mcqs = assignment_result_details.exclude(mcq_question=None)
    
    # mcqs checking
    # for result_detail_object in result_detail_mcqs:
    #     total_marks += result_detail_object.mcq_question.assignment.get_each_question_marks_in_assignment()
    #     if (result_detail_object.mcq_question.max_select < result_detail_object.mcq_selected_options.all().count()):
    #         raise ValidationError(f"the question with id {result_detail_object.mcq_question.id} only allows to be  {result_detail_object.mcq_question.max_select} options selected as max.")

    #     for selected_option in  result_detail_object.mcq_selected_options.all():
    #         if selected_option.is_correct:
    #             marks_obtained += result_detail_object.mcq_question.get_partial_marks()
    #     result_detail_object.marks = marks_obtained
    #     result_detail_object.save()

    
    # fractional_model_1 checking



    # result_detail_drop_downs = assignment_result_details.exclude(drop_down_question=None)
    # for result_detail_object in result_detail_drop_downs:
    #     total_marks += result_detail_object.drop_down_question.marks
    #     if result_detail_object.drop_down_selected_option:
    #         if result_detail_object.drop_down_selected_option.is_correct:
    #             marks_obtained += result_detail_object.drop_down_question.marks
    #             result_detail_object.marks = result_detail_object.drop_down_question.marks
    #             result_detail_object.save()


    # result_detail_drop_calculator = assignment_result_details.exclude(calculator_question=None)
    # for result_detail_object in result_detail_drop_calculator:
    #     total_marks += result_detail_object.calculator_question.marks
    #     if result_detail_object.calculator_question_answer == result_detail_object.calculator_question.answer:
    #         marks_obtained += result_detail_object.calculator_question.marks
    #         result_detail_object.marks = result_detail_object.calculator_question.marks
    #         result_detail_object.save()

    
    # result_detail_sorting_questions  = assignment_result_details.exclude(sorting_question=None)
    # for result_detail_object in result_detail_sorting_questions:
    #     total_marks += result_detail_object.sorting_question.assignment.get_marks()
    #     # check the sorting numbers are correct
    #     actual_options = result_detail_object.sorting_question.options.all().order_by("correct_sorting_number").values('id') 
    #     selected_options = result_detail_object.sorting_question_selected_options.all().values('id')
    #     if len(actual_options) == len(selected_options):
    #         marks_obtained += result_detail_object.sorting_question.assignment.get_marks()
    #         result_detail_object.marks = result_detail_object.sorting_question.assignment.get_marks()
    #         result_detail_object.save()


    # temp = 0
    # result_detail_fill_the_blank_questions = assignment_result_details.exclude(fill_in_the_blank_question=None)
    # for result_detail_object in result_detail_fill_the_blank_questions:
    #     single_correction = OptionFieldForFillinBlankQuestion.objects.filter(question__question=result_detail_object.fill_in_the_blank_question.pk).values('question').annotate(nums=Count("question")).filter(nums__gt=0).count()
    #     single_correction = result_detail_object.assignment.get_each_question_marks_in_assignment() / single_correction 
    #     total_marks += result_detail_object.fill_in_the_blank_question.assignment.get_each_question_marks_in_assignment()

    #     for option in result_detail_object.fill_in_the_blank_question_answers.all():
    #         if option.is_correct:
    #             marks_obtained += single_correction
    #             temp += single_correction
                
        # result_detail_object.marks = result_detail_object.fill_in_the_blank_question.get_each_question_marks_in_assignment()
        # result_detail_object.save()


    return AssignmentResult(assignment=assignment, student=student, marks_obtained=marks_obtained)