# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .column import MatrixColumnsMixin
from .question import Question


class QuestionMatrixdropdown(MatrixColumnsMixin, Question):
    """SurveyJS Multi-Select Matrix (matrixdropdown) question.

    `raw_value` is a dict mapping row names to dicts of column-name -> value.
    Example: {"row1": {"col1": "val1", "col2": "val2"}}

    The question declares no `inputType`, so its `value` is that same dict,
    unparsed. Individual *columns* may declare one, so `get_cell_value()` and
    `get_row_value()` parse per column.
    """

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

    def get_row_raw_value(self, row_name):
        """Get a row's cell dict, exactly as submitted."""
        val = self.raw_value
        if val and isinstance(val, dict):
            row = val.get(row_name, {})
            if isinstance(row, dict):
                return row
        return {}

    def get_row_value(self, row_name):
        """Get a row's cell dict, each cell parsed per its own column."""
        return self._parse_row(self.get_row_raw_value(row_name))

    def get_cell_raw_value(self, row_name, column_name):
        """Get a specific cell value, exactly as submitted."""
        return self.get_row_raw_value(row_name).get(column_name)

    def get_cell_value(self, row_name, column_name):
        """Get a specific cell value, parsed per its column's `inputType`."""
        raw = self.get_cell_raw_value(row_name, column_name)
        if raw is None:
            return None
        return self._parse_cell(column_name, raw)
