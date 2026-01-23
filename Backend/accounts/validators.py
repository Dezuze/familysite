from django.core.exceptions import ValidationError
import re

class ComplexPasswordValidator:
    """
    Validate whether the password meets the complexity requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one symbol
    """
    def validate(self, password, user=None):
        if len(password) < 12:
            raise ValidationError(
                "This password must contain at least 12 characters.",
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "This password must contain at least one uppercase letter.",
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "This password must contain at least one lowercase letter.",
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                "This password must contain at least one number.",
                code='password_no_number',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "This password must contain at least one symbol.",
                code='password_no_symbol',
            )

    def get_help_text(self):
        return (
            "Your password must contain at least 12 characters, "
            "and include at least one uppercase letter, "
            "one lowercase letter, one number, and one symbol."
        )
