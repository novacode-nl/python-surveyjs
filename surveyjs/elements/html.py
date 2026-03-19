# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .layout import Layout


class QuestionHtml(Layout):
    """SurveyJS HTML question.

    Displays static HTML content. Not an input element.
    """

    @property
    def is_question(self):
        """HTML elements are display-only, not input questions."""
        return False

    @property
    def html(self):
        """Get the HTML content."""
        return self.raw.get('html', '')
