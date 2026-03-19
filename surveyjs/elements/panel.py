# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from collections import OrderedDict

from .layout import Layout


class QuestionPanel(Layout):
    """SurveyJS Panel (layout container) question.

    Panels group questions together. They are not input elements themselves.
    """

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

    def load_data(self, data, is_form=False):
        """Load nested question data."""
        for element in self._layout_elements:
            if 'type' in element:
                element_obj = self.survey.get_element_object(element)
                if element_obj:
                    element_obj.load(
                        element_owner=self.element_owner,
                        parent=self,
                        data=data,
                        is_form=is_form,
                    )
