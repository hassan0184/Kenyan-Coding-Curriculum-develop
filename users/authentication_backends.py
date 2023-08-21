from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import InvalidToken, AuthenticationFailed
from .models import Student, Teacher
from django.utils.translation import gettext_lazy as _


class EdmazingJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        is_student = False
        try:
            if 'username' in validated_token:
                is_student = True
                student_id = validated_token[api_settings.USER_ID_CLAIM]
                student_username = validated_token['username']
            else:
                teacher_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(
                _("Token contained no recognizable user identification"))
        if is_student:
            try:
                user = Student.objects.get(
                    pk=student_id, username=student_username)
            except self.user_model.DoesNotExist:
                raise InvalidToken(
                    _("Student not found"), code="user_not_found")
        else:
            try:
                user = self.user_model.objects.get(
                    **{api_settings.USER_ID_FIELD: teacher_id})
            except self.user_model.DoesNotExist:
                raise InvalidToken(
                    _("Teacher not found"), code="user_not_found")
        if not user.is_active:
            raise AuthenticationFailed(
                _("User is inactive"), code="user_inactive")

        return user
