# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class commentQuestion(Question):
    """SurveyJS Comment (Long Text / Multi-line) question."""

    @property
    def max_length(self):
        return self.raw.get('maxLength', 0)

    @property
    def rows(self):
        """Number of visible rows in the text area."""
        return self.raw.get('rows', 4)

    @property
    def auto_grow(self):
        return self.raw.get('autoGrow', False)

    @property
    def allow_resize(self):
        return self.raw.get('allowResize', True)
