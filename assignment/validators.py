


def validate_file_extension(value,valid_extensions=['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls'],error_message='Unsupported file extension.'):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(error_message)




def validate_pdf(file):
    validate_file_extension(file,valid_extensions=['.pdf'],error_message='Unsupported file extension. Only .pdf is allowed')
    