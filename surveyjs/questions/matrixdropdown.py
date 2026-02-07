# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class matrixdropdownQuestion(Question):
    """SurveyJS Multi-Select Matrix (matrixdropdown) question.

    Value is a dict mapping row names to dicts of column-name -> value.
    Example: {"row1": {"col1": "val1", "col2": "val2"}}
    """

    @property
    def columns(self):
        """Get the matrix columns."""
        return self.raw.get('columns', [])

    @property
    def rows(self):
        """Get the matrix rows."""
        return self.raw.get('rows', [])

    @property
    def cell_type(self):
        """Default cell type for all columns: 'dropdown', 'checkbox',
        'radiogroup', 'text', 'comment', 'boolean', 'expression', 'rating'."""
        return self.raw.get('cellType', 'dropdown')

    @property
    def choices(self):
        """Default choices for all columns."""
        return self.raw.get('choices', [])

    @property
    def row_count(self):
        return len(self.rows)

    @property
    def column_count(self):
        return len(self.columns)

    def get_row_value(self, row_name):
        """Get the values dict for a specific row."""
        val = self.value
        if val and isinstance(val, dict):
            return val.get(row_name, {})
        return {}

    def get_cell_value(self, row_name, column_name):
        """Get a specific cell value."""
        row_val = self.get_row_value(row_name)
        if isinstance(row_val, dict):
            return row_val.get(column_name)
        return None
