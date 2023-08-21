from rest_framework.exceptions import NotFound
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from core.models import Class, School



class TeacherManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None, password2=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        teacher = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        teacher.set_password(password)
        teacher.save(using=self._db)
        return teacher

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        teacher = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        teacher.is_admin = True
        teacher.save(using=self._db)
        return teacher


class Teacher(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    secret_key = models.CharField(
        max_length=32, default='FKOUYO5AMZGSJLZ5G2QLZSJDEDRVUA7X')
    school = models.ForeignKey(to=School, on_delete=models.SET_NULL ,
                               related_name='teachers', null=True, blank=False, default=None)
    stripe_id = models.CharField(max_length=255,null=True)
    objects = TeacherManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    def get_all_students_of_class(self, class_id):
        if not self.classes.filter(pk=class_id):
            raise NotFound(
                f"teacher is not having any class haing id {class_id}")
        return self.classes.get(pk=class_id).students.all()


class StudentManager(BaseUserManager):
    def create_student(self, name, username, password, clas):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        student = self.model(
            name=name,
            username=username,
            clas=clas,
            password=password,
        )

        student.save(using=self._db)
        return student

    def all_in_class(self, class_id):
        return self.filter(clas=class_id)


class Student(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        null=True,
        unique=True,
    )
    name=models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    clas = models.ForeignKey(to=Class, on_delete=models.CASCADE,
                             related_name="students", null=True, blank=False, default=None)
    password = models.CharField(max_length=255)
    objects = StudentManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
