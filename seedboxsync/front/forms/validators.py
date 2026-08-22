#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms domain or IP validator."""

from ipaddress import ip_address
import re
from wtforms import ValidationError

# Python-compatible regex to validate domain names without variable-width lookbehinds.
DOMAIN_REGEX = re.compile(r"^(?:(?!-)[A-Za-z0-9-]{0,61}[A-Za-z0-9]\.)+[A-Za-z]{2,}$")


class DomainOrIP:
    """WTForms validator accepting either a valid domain name or an IP address."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize the DomainOrIP validator.

        Args:
            message: Custom validation error message. If not provided,
                a default error message will be used.
        """
        if not message:
            message = "Value must be a valid domain name or IP address."
        self.message = message

    def __call__(self, form: object, field: object) -> None:
        """Validate the input field content.

        Args:
            form: The WTForms form instance being validated.
            field: The field containing the data to validate.

        Raises:
            ValidationError: If the value is neither a valid IP address
                nor a valid domain name.
        """
        value = getattr(field, "data", "")

        if not value:
            return  # Let DataRequired/Optional handle empty fields

        # 1. Check if input is a valid IP address (IPv4 or IPv6)
        try:
            ip_address(value)
        except ValueError:
            pass
        else:
            return  # Valid IP address

        # 2. Check if input is a valid domain name
        if DOMAIN_REGEX.match(value):
            return  # Valid domain name

        # 3. Raise validation error if both checks fail
        raise ValidationError(self.message)
