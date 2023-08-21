from dataclasses import fields
from django.contrib import admin
from nested_admin import NestedModelAdmin, NestedInlineModelAdmin, NestedStackedInline, NestedTabularInline
from .models import (
    AssignedAssignment,
    Topic,
    Assignment,
    McqQuestion,
    McqOption,
    AssignmentResult,
    AssignmentResultDetail,
    FillInBlankQuestion,
    TextFieldForFillinBlankQuestion,
    OptionFieldForFillinBlankQuestion,
    SortingQuestion,
    SortingQuestionOptions,
    CalculatorQuestion,
    DropDownQuestion,
    DropDownOption,
    FillInBlankQuestion,
    TextFieldForFillinBlankQuestion,
    OptionFieldForFillinBlankQuestion,
    TestQuestion,
    FractionModel1,
    CalculatorQuestionAnswer,

)
# Register your models here.



class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_display = ('id', 'name', 'grade')
    list_filter = ('id', 'name', 'grade')


class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'question', 'is_correct')
    filter_display = ('id', 'text', 'question', 'is_correct')


class OptionInline(NestedTabularInline):
    model = McqOption
    extra = 1


class McqQuestionAdmin(admin.ModelAdmin):
    model = McqQuestion
    list_display = ('id', 'title', 'assignment')
    list_filter = ('id', 'title', 'assignment')
    inlines = [
        OptionInline,
    ]


class McqQuestionInline(NestedTabularInline):
    model = McqQuestion
    extra = 1
    classes = ['collapse']
    inlines = [
        OptionInline,
    ]


class FractionModel1Inline(NestedTabularInline):
    model = FractionModel1
    extra = 1
    classes = ['collapse']

class OptionforFillinBlankQuestionInline(NestedTabularInline):
    model = OptionFieldForFillinBlankQuestion
    extra = 1


class TextfieldInlineForFillInBlankQuestion(NestedTabularInline):
    model  = TextFieldForFillinBlankQuestion
    extra = 1
    inlines = [OptionforFillinBlankQuestionInline]
    

class FillInBlankQuestionInline(NestedTabularInline):
    model = FillInBlankQuestion
    extra = 1
    classes = ['collapse']
    inlines = [
        TextfieldInlineForFillInBlankQuestion,
    ]


class OptionforSortingQuestionInline(NestedTabularInline):
    model = SortingQuestionOptions
    extra = 1


class SortingQuestionInline(NestedTabularInline):
    model = SortingQuestion
    extra = 1
    classes = ['collapse']
    inlines = [
        OptionforSortingQuestionInline
    ]


class CalculatorQuestionAnswerInline(NestedTabularInline):
    model = CalculatorQuestionAnswer


class CalculatorQuestionModelAdmin(NestedTabularInline):
    model = CalculatorQuestion
    extra = 1
    classes = ['collapse']
    inlines = [
        CalculatorQuestionAnswerInline
    ]


class DropDownOptionModelAdmin(NestedTabularInline):
    model = DropDownOption
    extra = 1


class DropDownQuestionModelAdmin(NestedTabularInline):
    model = DropDownQuestion
    extra = 1
    classes = ['collapse']
    inlines = [DropDownOptionModelAdmin,]


class AssignmentAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'topic', '_type',
                    'is_pre_test', 'is_post_test')
    list_filter = ('id', 'name', 'topic', '_type',
                   'is_pre_test', 'is_post_test')
    classes = ['collapse']
    inlines = [
        McqQuestionInline,
        FillInBlankQuestionInline,
        SortingQuestionInline,
        CalculatorQuestionModelAdmin,
        DropDownQuestionModelAdmin,
        FractionModel1Inline,
    ]


class AssignedAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', '_class', 'from_date', 'to_date')


class AssignmentResultAdmin(admin.ModelAdmin):
    model = AssignmentResult
    list_display = ('student', 'assignment', 'marks_obtained', 'get_marks')
    list_filter = ('student', 'assignment', 'marks_obtained')

    def get_marks(self,obj):
        return obj.assignment.marks


class AssignmentResultDetailAdmin(admin.ModelAdmin):
    list_display = ('pk', 'student')


class DropDownQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk','text')

class DropDownOptionAdmin(admin.ModelAdmin):
    list_display = ('pk','text')


class FractionModel1Admin(admin.ModelAdmin):
    list_display = ('pk', 'text')

class CalculatorQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk','text')

class SortingQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text')


class SortingQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('pk',)


class FillTheBlankQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk',)


class TextFieldForFillTheBlankQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk','text')


class OptionFieldForFillTheBlankQuestionAdmin(admin.ModelAdmin):
    list_display = ('pk','is_correct')



admin.site.register(TestQuestion)
admin.site.register(FractionModel1, FractionModel1Admin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(McqQuestion, McqQuestionAdmin)
admin.site.register(McqOption, OptionAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignedAssignment, AssignedAssignmentAdmin)
admin.site.register(AssignmentResult, AssignmentResultAdmin)
admin.site.register(AssignmentResultDetail, AssignmentResultDetailAdmin)
admin.site.register(DropDownQuestion, DropDownQuestionAdmin)
admin.site.register(DropDownOption, DropDownOptionAdmin)
admin.site.register(CalculatorQuestion, CalculatorQuestionAdmin)
admin.site.register(SortingQuestion, SortingQuestionAdmin)
admin.site.register(SortingQuestionOptions, SortingQuestionOptionAdmin)
admin.site.register(FillInBlankQuestion, FillTheBlankQuestionAdmin)
admin.site.register(TextFieldForFillinBlankQuestion, TextFieldForFillTheBlankQuestionAdmin)
admin.site.register(OptionFieldForFillinBlankQuestion,OptionFieldForFillTheBlankQuestionAdmin)