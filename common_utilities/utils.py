from rest_framework.exceptions import NotFound, ValidationError
from django.conf import settings


def insert_assignment_result_detail(data, SerializerClass):
    assignment_result_detail_serializer = SerializerClass(data=data)
    assignment_result_detail_serializer.is_valid(True)
    return assignment_result_detail_serializer.save()
     


def get_object_or_not_found_exception(Klass, pk, message=None):
    obj = Klass.objects.filter(pk=pk).first()
    if message is None:
        message = f"No {Klass.__name__} with given id."
    if not obj:
        raise NotFound(message)
    return obj


def get_object_or_bad_request_exception(Klass, pk, message=None):
    obj = Klass.objects.filter(pk=pk).first()
    if message is None:
        message = f"No {Klass.__name__} with given id."
    if not obj:
        raise ValidationError(message)
    return obj


def get_pk_or_not_found_exception(Klass, pk, message=None):
    obj = Klass.objects.filter(pk=pk).first()
    if message is None:
        message = f"No {Klass.__name__} with given id."
    if not obj:
        raise NotFound(message)
    return pk


def get_value_from_dict_or_bad_request(dict, key, message=None):
    value = dict.get(key)
    if not value:
        raise ValidationError(f"{key} not found.")
    return value


def get_value_or_bad_request_exception(dict, key, message=None):
    value = dict.get(key)
    if value is None:
        raise ValidationError(f"{key} not found")
    return value


def serialize_data(Serializer, instance=None, data=None, many=False, **kwargs):
    if instance:
        serializer_obj = Serializer(instance=instance, many=many, **kwargs)
        return serializer_obj.data
    else:
        serializer_obj = Serializer(data=data, many=many, **kwargs)
        serializer_obj.is_valid()
        return serializer_obj.data


def build_url_for_file(file_path):

    domain = '''https://edmazingbucket.s3.us-west-2.amazonaws.com'''
    return f"{domain}/{file_path}"
