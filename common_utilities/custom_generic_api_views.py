from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from .custom_mixins import CustomCreateModelMixin


class CustomCreateAPIView(CustomCreateModelMixin,
                          GenericAPIView):
    """
    An extend class from custom CreateApiView class in order to
    define the status codes according to situation.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, self.status, *args, **kwargs)