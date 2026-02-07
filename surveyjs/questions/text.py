# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from datetime import date, datetime

from .question import Question


class textQuestion(Question):
    """SurveyJS Text (Single-Line Input) question.

    Supports inputType variants: text, number, date, datetime-local,
    email, url, password, tel, color, range, time, month, week.
    """

    @property
    def max_length(self):
        return self.raw.get('maxLength', 0)

    @property
    def min(self):
        return self.raw.get('min')

    @property
    def max(self):
        return self.raw.get('max')

    @property
    def step(self):
        return self.raw.get('step')

    @property
    def input_type(self):
        return self.raw.get('inputType', 'text')

    def to_number(self):
        """Convert value to a number (int or float).
        Applicable when inputType is 'number' or 'range'."""
        val = self.value
        if val is None:
            return None
        try:
            if isinstance(val, (int, float)):
                return val
            if '.' in str(val):
                return float(val)
            return int(val)
        except (ValueError, TypeError):
            return None

    def to_date(self):
        """Convert value to a date object.
        Applicable when inputType is 'date'."""
        val = self.value
        if val is None:
            return None
        if isinstance(val, date):
            return val
        try:
            return datetime.strptime(str(val), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    def to_datetime(self):
        """Convert value to a datetime object.
        Applicable when inputType is 'datetime-local'."""
        val = self.value
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(str(val), fmt)
            except ValueError:
                continue
        return None
