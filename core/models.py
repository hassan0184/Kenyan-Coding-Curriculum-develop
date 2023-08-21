from django.db import models
from django.apps import apps
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from common_utilities.choices import GradeLevelChoices
from django.apps import apps
from django.contrib import messages

class SchoolManager(models.Manager):
    def get_all_school_names(self):
        return self.only('name')


class School(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    
    objects = SchoolManager()

    def __str__(self) -> str:
        return f"{self.name}   {self.district}"
    class Meta:
        verbose_name_plural = "Approved Schools"

class RequestedSchool(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    is_approved= models.BooleanField(default=False)
    requested_teacher=models.ForeignKey('users.Teacher',on_delete=models.DO_NOTHING)

    objects = SchoolManager()

    def __str__(self) -> str:
        return f"{self.name} {self.type}  {self.district}"
    def save(self, *args, **kwargs):
        if self.is_approved == True:
             already_exist=School.objects.filter(name=self.name)
             if not already_exist:
              School.objects.create(name=self.name,type=self.type,district=self.district)
              MyModel = apps.get_model('users', 'Teacher')
              teacher_object=MyModel.objects.get(id=self.requested_teacher.id)
              regestered_school_object=School.objects.get(name=self.name)
              teacher_object.school=regestered_school_object
              teacher_object.save()
              self.delete()
             else:
                pass
        else:
            
            super(RequestedSchool, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = "Requested Schools"


class Grade(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.name

class ClassManager(models.Manager):
    pass



class Class(models.Model):
    name = models.CharField(max_length=255)
    grade_level = models.ForeignKey(to=Grade,on_delete=models.CASCADE)
    no_of_students = models.IntegerField(default=30)
    school = models.ForeignKey(
        to=School, on_delete=models.CASCADE, related_name="classes")
    teacher = models.ForeignKey(
        to='users.Teacher', on_delete=models.CASCADE, related_name='classes', null=True)

    objects = ClassManager()

    class Meta:
        unique_together = ('name', 'grade_level')

    def __str__(self) -> str:
        return f"{self.name}  {self.grade_level}"

    def get_all_assigned_assignments(self):
        """will return all assignments assigned to class """
        return self.assigned_assignments.all().values_list('assignment')
    
    def get_grade_level_display(self):
        return self.grade_level.name



class Post(models.Model):
    name = models.CharField(max_length=255)



class RequestQoute(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    title = models.ForeignKey(to="Post", on_delete=models.CASCADE)
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    school = models.ForeignKey(to="School", on_delete=models.CASCADE)
    description = models.TextField()