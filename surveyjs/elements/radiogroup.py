# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionRadiogroup(Question):
    """SurveyJS Radio Button Group question."""

    @property
    def choices(self):
        """Get the list of choices."""
        return self.raw.get('choices', [])

    @property
    def choices_values(self):
        """Get normalized choice values as a list of dicts with 'value' and 'text'."""
        return [self.choice_item(choice) for choice in self.choices]

    @property
    def value(self):
        """The picked choice value. With a choice comment, SurveyJS stores
        `{"value": ..., "comment": ...}`; this is the plain value, the comment
        is in `choice_comments`."""
        return self._unwrap_choice(self.raw_value)

    @property
    def value_text(self):
        """Get the display text for the current value."""
        val = self.value
        if val is None:
            return None
        return self._choice_text(val, {c['value']: c['text'] for c in self.choices_values})

    @property
    def has_none(self):
        """Whether the 'None' option is enabled."""
        return self.raw.get('showNoneItem', self.raw.get('hasNone', False))

    @property
    def choices_order(self):
        return self.raw.get('choicesOrder', 'none')

    @property
    def col_count(self):
        return self.raw.get('colCount', 0)

    def value_spec(self):
        """One choice value. A choice with its own comment area may also be
        stored as `{"value": ..., "comment": ...}`, as SurveyJS does once a
        comment is typed; the spec accepts both forms then (`anyOf`)."""
        return self._choices_spec()
