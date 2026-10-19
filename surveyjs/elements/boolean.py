# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .inputtype import parse_boolean
from .question import Question


class QuestionBoolean(Question):
    """SurveyJS Boolean (Yes/No) question.

    `raw_value` is True/False, or the schema's `valueTrue`/`valueFalse`;
    `value` is always a Python bool (or None).
    """

    @property
    def label_true(self):
        return self.translate(self.raw.get('labelTrue', 'Yes'))

    @property
    def label_false(self):
        return self.translate(self.raw.get('labelFalse', 'No'))

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

    @property
    def value(self):
        """`raw_value` as a Python bool, honouring `valueTrue`/`valueFalse`.

        None when unanswered or when the submitted value is unrecognised —
        check `raw_value` to tell the two apart."""
        val = self.raw_value
        if val is None:
            return None
        try:
            return parse_boolean(val, self.value_true, self.value_false)
        except ValueError:
            return None

    @property
    def value_text(self):
        """Get the display text for the current value: `label_true` or
        `label_false`, or None when unanswered or unrecognised."""
        val = self.value
        if val is None:
            return None
        return self.label_true if val else self.label_false

    def to_bool(self):
        """Convert the value to a Python bool (same as `value`)."""
        return self.value

    def value_spec(self):
        """True/False, or the schema's own `valueTrue`/`valueFalse`."""
        if 'valueTrue' in self.raw or 'valueFalse' in self.raw:
            return {'enum': [self.value_true, self.value_false]}
        return {'type': 'boolean'}
