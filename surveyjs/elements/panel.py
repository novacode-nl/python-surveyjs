# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .layout import Layout


class QuestionPanel(Layout):
    """SurveyJS Panel (layout container) question.

    Panels group questions together. They are not input elements themselves.
    """

    @property
    def state(self):
        """Panel state: 'default', 'collapsed', or 'expanded'."""
        return self.raw.get('state', 'default')

    @property
    def inner_indent(self):
        return self.raw.get('innerIndent', 0)

    def load_data(self, data, is_form=False):
        """Build the nested child elements and load their submission data.

        Only on the form path. The Creator walks nested elements itself (see
        `SurveyCreator._load_elements`) so that it can register them into its
        flat registries as it goes; building them here too would construct
        every panel child twice and discard the first copy.
        """
        if not is_form:
            return

        # A panel nested inside a materialised panel instance repeats with its
        # row, so its children must not be filed by name on the owner either.
        register_with_owner = not self.in_repeating_context

        for element in self._layout_elements:
            if 'type' in element:
                element_obj = self.survey.get_element_object(element)
                if element_obj:
                    element_obj.load(
                        element_owner=self.element_owner,
                        parent=self,
                        data=data,
                        is_form=is_form,
                        register_with_owner=register_with_owner,
                    )
