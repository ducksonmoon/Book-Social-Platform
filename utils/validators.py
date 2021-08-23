from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

def validate_username(username:str) -> bool:
    """ Validate a given username. """
    SPECIAL_CHARACTERS_IN = "!@#$%^&*()+=-`~,/'[]<>?{}|\\ "
    SPECIAL_CHARACTERS_START = "!@#$%^&*()+=-`~,./'[]<>?{}|\\"
    if len(username) < 3:
        return False
    if username[0] in SPECIAL_CHARACTERS_START:
        return False
    for char in username:
        if char in SPECIAL_CHARACTERS_IN:
            return False
    return True

def validate_email(email:str) -> bool:
    """ Validate a given email. """
    # Email Validator
    # https://stackoverflow.com/questions/8022530/python-check-for-valid-email-address
    # https://stackoverflow.com/questions/7160737/python-how-to-validate-an-email-address-using-a-regular-expression
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if not EMAIL_REGEX.match(email):
        return False
    return True


def validate_image_extension(value:str) -> bool:
    """ Validate a given image extension. """
    # Support: jpg, png, jpeg
    SUPPORTED_EXTENSIONS = ["jpg", "png", "jpeg"]
    if value.split(".")[-1].lower() not in SUPPORTED_EXTENSIONS:
        raise ValidationError(f"{value.name} is not a supported image extension.")
    return True

