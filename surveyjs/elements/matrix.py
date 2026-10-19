# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionMatrix(Question):
    """SurveyJS Single-Select Matrix question.

    Value is a dict mapping row names to selected column values.
    Example: {"row1": "col2", "row2": "col1"}
    """

    @property
    def columns(self):
        """Get the matrix columns."""
        return self.raw.get('columns', [])

    @property
    def column_values(self):
        """Normalized column values."""
        return [self.choice_item(col) for col in self.columns]

    @property
    def rows(self):
        """Get the matrix rows."""
        return self.raw.get('rows', [])

    @property
    def row_values(self):
        """Normalized row values."""
        return [self.choice_item(row) for row in self.rows]

    @property
    def is_all_row_required(self):
        return self.raw.get('isAllRowRequired', False)

    def get_row_value(self, row_name):
        """Get the selected value for a specific row."""
        val = self.value
        if val and isinstance(val, dict):
            return val.get(row_name)
        return None

    def value_spec(self):
        """An object keyed by row value, each row holding one column value."""
        columns = {'enum': [column['value'] for column in self.column_values]}
        return {
            'type': 'object',
            'properties': {row['value']: columns for row in self.row_values},
            'additionalProperties': False,
        }
