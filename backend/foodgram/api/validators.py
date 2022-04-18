from rest_framework.serializers import ValidationError

from .variables import ERROR_MESSAGE_PASSWORD

MIN_PASS_SYMBOLS = 4

def check_pass(password):
    if password == '' or len(password) < MIN_PASS_SYMBOLS:
        raise ValidationError(
            ERROR_MESSAGE_PASSWORD
        )

