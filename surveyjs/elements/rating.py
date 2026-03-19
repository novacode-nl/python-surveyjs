# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionRating(Question):
    """SurveyJS Rating Scale question.

    Value is typically a number or string from the rate values.
    """

    @property
    def rate_min(self):
        return self.raw.get('rateMin', 1)

    @property
    def rate_max(self):
        return self.raw.get('rateMax', 5)

    @property
    def rate_step(self):
        return self.raw.get('rateStep', 1)

    @property
    def rate_values(self):
        """Custom rate values, if specified."""
        return self.raw.get('rateValues', [])

    @property
    def rate_count(self):
        return self.raw.get('rateCount', 5)

    @property
    def min_rate_description(self):
        return self.raw.get('minRateDescription', '')

    @property
    def max_rate_description(self):
        return self.raw.get('maxRateDescription', '')

    @property
    def display_mode(self):
        """'auto', 'buttons', or 'dropdown'."""
        return self.raw.get('displayMode', 'auto')

    @property
    def rate_type(self):
        """'labels', 'stars', or 'smileys'."""
        return self.raw.get('rateType', 'labels')

    def to_number(self):
        """Convert value to a number."""
        val = self.value
        if val is None:
            return None
        try:
            if isinstance(val, (int, float)):
                return val
            return int(val)
        except (ValueError, TypeError):
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
