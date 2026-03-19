# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .element import Element


class Layout(Element):
    """
    Base class for all SurveyJS layout types.
    """

    @property
    def is_question(self):
        """Panels are layout elements, not input questions."""
        return False

    @property
    def is_input(self):
        """Panels are layout elements, not input questions."""
        return False

    @property
    def _layout_elements(self):
        """Get the raw nested elements."""
        return self.raw.get('elements', [])
