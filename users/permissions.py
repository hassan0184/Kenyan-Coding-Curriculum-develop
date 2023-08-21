from rest_framework.permissions import BasePermission



class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if request.user.__class__.__name__ == "Student":
            return True
        return False


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return True if request.user.__class__.__name__ == "Teacher" else False