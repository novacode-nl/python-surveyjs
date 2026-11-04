# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionDropdown(Question):
    """SurveyJS Dropdown (single-select) question."""

    @property
    def choices(self):
        return self.raw.get("choices", [])

    @property
    def choices_values(self):
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
        return self._choice_text(val, {c["value"]: c["text"] for c in self.choices_values})

    @property
    def choices_by_url(self):
        """Get choices loaded from a URL configuration."""
        return self.raw.get("choicesByUrl", None)

    @property
    def search_enabled(self):
        return self.raw.get("searchEnabled", True)

    @property
    def placeholder_text(self):
        return self.translate(self.raw.get("placeholder", ""))

    @property
    def allow_clear(self):
        return self.raw.get("allowClear", True)

    def value_spec(self):
        """One choice value. A choice with its own comment area may also be
        stored as `{"value": ..., "comment": ...}`, as SurveyJS does once a
        comment is typed; the spec accepts both forms then (`anyOf`)."""
        return self._choices_spec()
