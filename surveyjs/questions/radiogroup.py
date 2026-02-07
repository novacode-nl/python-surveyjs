# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class radiogroupQuestion(Question):
    """SurveyJS Radio Button Group question."""

    @property
    def choices(self):
        """Get the list of choices."""
        return self.raw.get('choices', [])

    @property
    def choices_values(self):
        """Get normalized choice values as a list of dicts with 'value' and 'text'."""
        result = []
        for choice in self.choices:
            if isinstance(choice, dict):
                result.append({
                    'value': choice.get('value'),
                    'text': choice.get('text', str(choice.get('value', '')))
                })
            else:
                result.append({'value': choice, 'text': str(choice)})
        return result

    @property
    def value_text(self):
        """Get the display text for the current value."""
        val = self.value
        for choice in self.choices_values:
            if choice['value'] == val:
                return choice['text']
        return str(val) if val is not None else None

    @property
    def has_other(self):
        """Whether the 'Other' option is enabled."""
        return self.raw.get('showOtherItem', self.raw.get('hasOther', False))

    @property
    def other_text(self):
        return self.raw.get('otherText', 'Other')

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
