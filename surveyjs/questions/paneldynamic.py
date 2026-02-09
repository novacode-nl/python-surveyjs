# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionPaneldynamic(Question):
    """SurveyJS Dynamic Panel question.

    Allows users to add/remove groups of questions (panels).
    Value is a list of dicts, each dict representing one panel instance.
    """

    @property
    def template_elements(self):
        """Template elements that repeat for each panel."""
        return self.raw.get('templateElements', self.raw.get('elements', []))

    @property
    def panel_count(self):
        """Initial panel count."""
        return self.raw.get('panelCount', 1)

    @property
    def min_panel_count(self):
        return self.raw.get('minPanelCount', 0)

    @property
    def max_panel_count(self):
        return self.raw.get('maxPanelCount', None)

    @property
    def panel_add_text(self):
        return self.raw.get('panelAddText', 'Add New')

    @property
    def panel_remove_text(self):
        return self.raw.get('panelRemoveText', 'Remove')

    @property
    def allow_add_panel(self):
        return self.raw.get('allowAddPanel', True)

    @property
    def allow_remove_panel(self):
        return self.raw.get('allowRemovePanel', True)

    @property
    def template_title(self):
        return self.raw.get('templateTitle', '')

    @property
    def panels_data(self):
        """Get the value as a list of dicts (panel instances)."""
        val = self.value
        if isinstance(val, list):
            return val
        return []

    @property
    def actual_panel_count(self):
        """Number of actual panel instances in the data."""
        return len(self.panels_data)

    def get_panel_value(self, panel_index, field_name):
        """Get a specific field value from a panel instance.

        Args:
            panel_index: Zero-based index of the panel instance.
            field_name: Name of the field within the panel.

        Returns:
            The value of the field, or None.
        """
        data = self.panels_data
        if panel_index < len(data) and isinstance(data[panel_index], dict):
            return data[panel_index].get(field_name)
        return None
