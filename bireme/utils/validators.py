from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

import datetime

def valid_min_year(date):
    # avoid internal system error (datetime methods require year >= 1900)
    min_valid_date = datetime.date(1900, 1, 1)

    if date < min_valid_date:
        raise ValidationError(
            _('Year must be greater than 1900')
        )
