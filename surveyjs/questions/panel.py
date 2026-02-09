# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from collections import OrderedDict

from .question import Question


class QuestionPanel(Question):
    """SurveyJS Panel (layout container) question.

    Panels group questions together. They are not input elements themselves.
    """

    @property
    def is_input(self):
        """Panels are layout elements, not input questions."""
        return False

    @property
    def panel_title(self):
        return self.raw.get('title', '')

    @property
    def state(self):
        """Panel state: 'default', 'collapsed', or 'expanded'."""
        return self.raw.get('state', 'default')

    @property
    def inner_indent(self):
        return self.raw.get('innerIndent', 0)

    @property
    def elements(self):
        """Get the raw nested elements."""
        return self.raw.get('elements', [])

    def load_data(self, data, is_form=False):
        """Load nested question data."""
        for element in self.elements:
            if 'type' in element:
                question_obj = self.survey.get_question_object(element)
                if question_obj:
                    question_obj.load(
                        question_owner=self.question_owner,
                        parent=self,
                        data=data,
                        is_form=is_form,
                    )
