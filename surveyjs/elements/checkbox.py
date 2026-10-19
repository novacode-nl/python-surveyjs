# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionCheckbox(Question):
    """SurveyJS Checkbox (multiple selection) question.

    Value is typically a list of selected choice values.
    """

    @property
    def choices(self):
        return self.raw.get('choices', [])

    @property
    def choices_values(self):
        """Get normalized choice values as a list of dicts."""
        return [self.choice_item(choice) for choice in self.choices]

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
    def has_none(self):
        return self.raw.get('showNoneItem', self.raw.get('hasNone', False))

    @property
    def has_select_all(self):
        return self.raw.get('showSelectAllItem', self.raw.get('hasSelectAll', False))

    @property
    def max_selected_choices(self):
        return self.raw.get('maxSelectedChoices', 0)

    @property
    def min_selected_choices(self):
        return self.raw.get('minSelectedChoices', 0)

    @property
    def col_count(self):
        return self.raw.get('colCount', 0)

    def value_spec(self):
        """A list of choice values."""
        spec = self._choices_spec(multiple=True)
        if self.max_selected_choices:
            spec['maxItems'] = self.max_selected_choices
        return spec
