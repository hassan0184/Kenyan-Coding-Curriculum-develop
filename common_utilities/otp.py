from django.conf import settings
import pyotp

OTP_RESET_TIMEOUT = settings.OTP_RESET_TIMEOUT

def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key, interval=OTP_RESET_TIMEOUT)
    return totp.now()


def verify_otp(secret_key, otp):
    totp = pyotp.TOTP(secret_key, interval=OTP_RESET_TIMEOUT)
    return totp.verify(otp,valid_window=50)
