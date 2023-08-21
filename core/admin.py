from django.contrib import admin
from .models import School, Class, Grade, Post,RequestedSchool
from django.utils.translation import ngettext
from django.contrib import messages
from rest_framework.response import Response
from users.models import Teacher






class ClassAdminModel(admin.ModelAdmin):
    list_display = ["pk","name", "grade_level", "no_of_students","school","teacher"]


class GradeAdminModel(admin.ModelAdmin):
    list_display = ["pk","name"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["pk", "name"]


@admin.action(description='Mark selected School as Approved')
def make_approved(self, request, queryset):
    for obj in queryset:
     try:
        
        School.objects.create(name=obj.name,type=obj.type,district=obj.district)
        teacher_object=Teacher.objects.get(id=obj.requested_teacher.id)
        regestered_school_object=School.objects.get(name=obj.name)
        teacher_object.school=regestered_school_object
        teacher_object.save()
        obj.delete()
        messages.success(request,'School with the Name [' + obj.name + '] has been Approved.')
     except Exception as e:
        messages.error(request,'School with the Name [' + obj.name + '] already Exists.')

    
    
    





class SchoolAdmin(admin.ModelAdmin):
    list_display=['name','type','district']
    
class RequestedSchoolAdmin(admin.ModelAdmin):
    list_display=['is_approved','name','type','district']
    actions = [make_approved]
admin.site.register(School, SchoolAdmin)
admin.site.register(RequestedSchool, RequestedSchoolAdmin)
admin.site.register(Class, ClassAdminModel)
admin.site.register(Grade, GradeAdminModel)
admin.site.register(Post, PostAdmin)
