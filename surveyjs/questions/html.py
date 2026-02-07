# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class htmlQuestion(Question):
    """SurveyJS HTML question.

    Displays static HTML content. Not an input element.
    """

    @property
    def is_input(self):
        """HTML elements are display-only, not input questions."""
        return False

    @property
    def html(self):
        """Get the HTML content."""
        return self.raw.get('html', '')
