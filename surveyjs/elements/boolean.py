# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionBoolean(Question):
    """SurveyJS Boolean (Yes/No) question.

    Value is typically True/False.
    """

    @property
    def label_true(self):
        return self.raw.get('labelTrue', 'Yes')

    @property
    def label_false(self):
        return self.raw.get('labelFalse', 'No')

    @property
    def value_true(self):
        return self.raw.get('valueTrue', True)

    @property
    def value_false(self):
        return self.raw.get('valueFalse', False)

    @property
    def render_as(self):
        """Render mode: 'default' (toggle) or 'checkbox' or 'radio'."""
        return self.raw.get('renderAs', 'default')

    def to_bool(self):
        """Convert the value to a Python bool."""
        val = self.value
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        if val == self.value_true:
            return True
        if val == self.value_false:
            return False
        # Fallback
        return bool(val)
