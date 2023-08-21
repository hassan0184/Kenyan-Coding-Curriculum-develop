from .custom_exceptions import ServiceUnavailable
from django.core.mail import EmailMessage, send_mail
import os


class SendEmail:
    @staticmethod
    def send_email(data, filename = None, file=None, file_type="text/csv"):
        try:
            email = EmailMessage(
                subject=data["email_subject"],
                body=data["body"],
                from_email=os.environ.get("EMAIL_FROM"),
                to=[data['to_email']]
            )
            if file:
                email.attach(filename, file.getvalue(),file_type)
            email.send()
            return True
        except Exception as e:
            raise ServiceUnavailable("Unable to send the email.") 

    