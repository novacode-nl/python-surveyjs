# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .column import MatrixColumnsMixin
from .question import Question


class QuestionMatrixdynamic(MatrixColumnsMixin, Question):
    """SurveyJS Dynamic Matrix (matrixdynamic) question.

    `raw_value` is a list of dicts, each mapping column names to values.
    Example: [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]

    The question declares no `inputType`, so its `value` is that same list,
    unparsed. Individual *columns* may declare one, so `get_cell_value()` and
    `get_row_value()` parse per column, while `rows_data` stays as submitted.
    """

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
        """Get the list of row data dicts, exactly as submitted."""
        val = self.raw_value
        if val and isinstance(val, list):
            return val
        return []

    @property
    def actual_row_count(self):
        """Number of rows in submitted data."""
        return len(self.rows_data)

    def get_row_raw_value(self, row_index):
        """Get a row's cell dict, exactly as submitted."""
        data = self.rows_data
        if 0 <= row_index < len(data) and isinstance(data[row_index], dict):
            return data[row_index]
        return {}

    def get_row_value(self, row_index):
        """Get a row's cell dict, each cell parsed per its own column."""
        return self._parse_row(self.get_row_raw_value(row_index))

    def get_cell_raw_value(self, row_index, column_name):
        """Get a specific cell value, exactly as submitted."""
        return self.get_row_raw_value(row_index).get(column_name)

    def get_cell_value(self, row_index, column_name):
        """Get a specific cell value, parsed per its column's `inputType`."""
        raw = self.get_cell_raw_value(row_index, column_name)
        if raw is None:
            return None
        return self._parse_cell(column_name, raw)
