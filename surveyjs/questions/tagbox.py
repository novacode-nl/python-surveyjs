# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class tagboxQuestion(Question):
    """SurveyJS Tag Box (multi-select dropdown) question.

    Value is typically a list of selected values.
    """

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
    def value_texts(self):
        """Get the display texts for the currently selected values."""
        val = self.value
        if not val or not isinstance(val, list):
            return []
        texts = []
        choice_map = {c['value']: c['text'] for c in self.choices_values}
        for v in val:
            texts.append(choice_map.get(v, str(v)))
        return texts

    @property
    def has_other(self):
        return self.raw.get('showOtherItem', self.raw.get('hasOther', False))

    @property
    def search_enabled(self):
        return self.raw.get('searchEnabled', True)

    @property
    def max_selected_choices(self):
        return self.raw.get('maxSelectedChoices', 0)
