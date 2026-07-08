# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .inputtype import (
    parse_date,
    parse_datetime,
    parse_month,
    parse_number,
    parse_time,
    parse_week,
)
from .question import Question


class QuestionText(Question):
    """SurveyJS Text (Single-Line Input) question.

    Supports inputType variants: text, number, date, datetime-local,
    email, url, password, tel, color, range, time, month, week.

    `value` parses `raw_value` according to `input_type`. The `to_*` methods
    below parse `raw_value` as a specific type regardless of `input_type`,
    for when you know better than the schema does.
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

    def _parse_as(self, parser):
        """Parse this question's `raw_value` with `parser`, or None.

        Deliberately reads `raw_value`, not `value`: these methods exist to
        parse as a named type *regardless* of the declared `inputType`, and
        `value` has already been parsed (or nulled) according to it."""
        value = self.raw_value
        if value is None:
            return None
        try:
            return parser(value)
        except (ValueError, TypeError, AttributeError, IndexError, KeyError):
            return None

    def to_number(self):
        """Convert value to a number (int or float).
        Applicable when inputType is 'number' or 'range'."""
        return self._parse_as(parse_number)

    def to_date(self):
        """Convert value to a date object.
        Applicable when inputType is 'date'."""
        return self._parse_as(parse_date)

    def to_datetime(self):
        """Convert value to a datetime object.
        Applicable when inputType is 'datetime-local'."""
        return self._parse_as(parse_datetime)

    def to_time(self):
        """Convert value to a time object.
        Applicable when inputType is 'time'."""
        return self._parse_as(parse_time)

    def to_month(self):
        """Convert value to a date object at the first of the month.
        Applicable when inputType is 'month'."""
        return self._parse_as(parse_month)

    def to_week(self):
        """Convert value to a date object at the Monday of the ISO week.
        Applicable when inputType is 'week'."""
        return self._parse_as(parse_week)
