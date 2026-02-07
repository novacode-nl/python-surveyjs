# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class expressionQuestion(Question):
    """SurveyJS Expression question.

    A read-only calculated field. Value is computed from an expression.
    """

    @property
    def expression(self):
        """The calculation expression."""
        return self.raw.get('expression', '')

    @property
    def display_style(self):
        """'none', 'decimal', 'currency', or 'percent'."""
        return self.raw.get('displayStyle', 'none')

    @property
    def currency(self):
        return self.raw.get('currency', 'USD')

    @property
    def maximum_fraction_digits(self):
        return self.raw.get('maximumFractionDigits', -1)

    @property
    def minimum_fraction_digits(self):
        return self.raw.get('minimumFractionDigits', -1)

    @property
    def use_grouping(self):
        return self.raw.get('useGrouping', True)

    def to_number(self):
        """Try to convert the expression value to a number."""
        val = self.value
        if val is None:
            return None
        try:
            if isinstance(val, (int, float)):
                return val
            return float(val)
        except (ValueError, TypeError):
            return None
