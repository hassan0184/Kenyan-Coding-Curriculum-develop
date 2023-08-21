from django.contrib import admin
from .models import Teacher, Student
# Register your models here.



class StudentAdmin(admin.ModelAdmin):
    list_display = ('id','username','clas','password')
    search_fields = ['username','clas__name']
   


admin.site.register(Teacher)
admin.site.register(Student,StudentAdmin)