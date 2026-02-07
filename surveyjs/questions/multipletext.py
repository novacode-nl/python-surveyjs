# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class multipletextQuestion(Question):
    """SurveyJS Multiple Textboxes question.

    Value is a dict mapping item names to their values.
    Example: {"firstName": "John", "lastName": "Doe"}
    """

    @property
    def items(self):
        """Get the list of text items definitions."""
        return self.raw.get('items', [])

    @property
    def item_names(self):
        """Get the list of item names."""
        return [item.get('name', '') for item in self.items]

    @property
    def item_count(self):
        return len(self.items)

    @property
    def col_count(self):
        return self.raw.get('colCount', 1)

    def get_item_value(self, item_name):
        """Get the value for a specific item by name."""
        val = self.value
        if val and isinstance(val, dict):
            return val.get(item_name)
        return None

    def get_item_title(self, item_name):
        """Get the title for a specific item by name."""
        for item in self.items:
            if item.get('name') == item_name:
                return item.get('title', item_name)
        return item_name
