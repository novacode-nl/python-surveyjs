# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class dropdownQuestion(Question):
    """SurveyJS Dropdown (single-select) question."""

    @property
    def choices(self):
        return self.raw.get('choices', [])

    @property
    def choices_values(self):
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
        return self.raw.get('showOtherItem', self.raw.get('hasOther', False))

    @property
    def other_text(self):
        return self.raw.get('otherText', 'Other')

    @property
    def choices_by_url(self):
        """Get choices loaded from a URL configuration."""
        return self.raw.get('choicesByUrl', None)

    @property
    def search_enabled(self):
        return self.raw.get('searchEnabled', True)

    @property
    def placeholder_text(self):
        return self.raw.get('placeholder', '')

    @property
    def allow_clear(self):
        return self.raw.get('allowClear', True)
