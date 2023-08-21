from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin


class CustomCreateModelMixin(CreateModelMixin):
    """
    Create a model instance.
    """

    def create(self, request, status=status.HTTP_201_CREATED, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status, headers=headers)
