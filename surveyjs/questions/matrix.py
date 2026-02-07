# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class matrixQuestion(Question):
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
        result = []
        for col in self.columns:
            if isinstance(col, dict):
                result.append({
                    'value': col.get('value'),
                    'text': col.get('text', str(col.get('value', '')))
                })
            else:
                result.append({'value': col, 'text': str(col)})
        return result

    @property
    def rows(self):
        """Get the matrix rows."""
        return self.raw.get('rows', [])

    @property
    def row_values(self):
        """Normalized row values."""
        result = []
        for row in self.rows:
            if isinstance(row, dict):
                result.append({
                    'value': row.get('value'),
                    'text': row.get('text', str(row.get('value', '')))
                })
            else:
                result.append({'value': row, 'text': str(row)})
        return result

    @property
    def is_all_row_required(self):
        return self.raw.get('isAllRowRequired', False)

    def get_row_value(self, row_name):
        """Get the selected value for a specific row."""
        val = self.value
        if val and isinstance(val, dict):
            return val.get(row_name)
        return None
