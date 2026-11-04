# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionCheckbox(Question):
    """SurveyJS Checkbox (multiple selection) question.

    Value is typically a list of selected choice values.
    """

    supports_elements_in_choice = True

    @property
    def choices(self):
        return self.raw.get("choices", [])

    @property
    def choices_values(self):
        """Get normalized choice values as a list of dicts."""
        return [self.choice_item(choice) for choice in self.choices]

    @property
    def value_property_name(self):
        """`valuePropertyName`: store each picked item as an object with the
        choice value under this key, e.g. `[{"car": "Ford"}]`. '' when not set."""
        return self.raw.get("valuePropertyName", "")

    @property
    def value(self):
        """The picked choice values, as a list of plain values. SurveyJS
        stores objects when `valuePropertyName` is set or a choice has its own
        comment area; their comments are in `choice_comments`."""
        value = self.raw_value
        if not isinstance(value, list):
            return value
        return [self._unwrap_choice(item) for item in value]

    @property
    def _choice_value_field(self):
        return self.value_property_name or super()._choice_value_field

    def _item_object_field(self):
        if self.value_property_name:
            return self.value_property_name
        return self._choice_value_field if self._has_choice_comments() else ""

    @property
    def value_texts(self):
        """Get the display texts for the currently selected values."""
        val = self.value
        if not val or not isinstance(val, list):
            return []
        choice_map = {c["value"]: c["text"] for c in self.choices_values}
        return [self._choice_text(v, choice_map) for v in val]

    @property
    def has_none(self):
        return self.raw.get("showNoneItem", self.raw.get("hasNone", False))

    @property
    def has_select_all(self):
        return self.raw.get("showSelectAllItem", self.raw.get("hasSelectAll", False))

    @property
    def max_selected_choices(self):
        return self.raw.get("maxSelectedChoices", 0)

    @property
    def min_selected_choices(self):
        return self.raw.get("minSelectedChoices", 0)

    @property
    def col_count(self):
        return self.raw.get("colCount", 0)

    def value_spec(self):
        """A list of choice values, or of objects (`[{"car": "Ford"}]`) when
        `valuePropertyName` is set or a choice has its own comment area: the
        form SurveyJS stores. `value` returns the plain choice values."""
        spec = self._choices_spec(multiple=True)
        if self.max_selected_choices:
            spec["maxItems"] = self.max_selected_choices
        return spec
