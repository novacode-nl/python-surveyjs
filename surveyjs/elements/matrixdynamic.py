# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionMatrixdynamic(Question):
    """SurveyJS Dynamic Matrix (matrixdynamic) question.

    Value is a list of dicts, where each dict maps column names to values.
    Example: [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
    """

    @property
    def columns(self):
        """Get the matrix columns."""
        return self.raw.get('columns', [])

    @property
    def row_count(self):
        """Initial/current number of rows."""
        return self.raw.get('rowCount', 2)

    @property
    def min_row_count(self):
        return self.raw.get('minRowCount', 0)

    @property
    def max_row_count(self):
        return self.raw.get('maxRowCount', 1000)

    @property
    def add_row_text(self):
        return self.raw.get('addRowText', '')

    @property
    def remove_row_text(self):
        return self.raw.get('removeRowText', '')

    @property
    def cell_type(self):
        return self.raw.get('cellType', 'dropdown')

    @property
    def choices(self):
        return self.raw.get('choices', [])

    @property
    def rows_data(self):
        """Get the list of row data dicts."""
        val = self.value
        if val and isinstance(val, list):
            return val
        return []

    @property
    def actual_row_count(self):
        """Number of rows in submitted data."""
        return len(self.rows_data)

    def get_cell_value(self, row_index, column_name):
        """Get a specific cell value by row index and column name."""
        data = self.rows_data
        if 0 <= row_index < len(data):
            return data[row_index].get(column_name)
        return None
