# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .column import MatrixColumnsMixin
from .question import Question


class QuestionMatrixdropdown(MatrixColumnsMixin, Question):
    """SurveyJS Multi-Select Matrix (matrixdropdown) question.

    `raw_value` is a dict mapping row names to dicts of column-name -> value.
    Example: {"row1": {"col1": "val1", "col2": "val2"}}

    `value` is that dict with each cell parsed per its own column (a date
    column's `inputType`, a boolean column's `valueTrue`/`valueFalse`), as
    are `get_cell_value()` and `get_row_value()`.
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

    @property
    def row_names(self):
        """The name of each row, in schema order.

        A row is authored either as a bare value or as `{'value': …, 'text': …}`,
        and it is the value that keys the submitted data.
        """
        names = []
        for row in self.rows:
            name = row.get('value') if isinstance(row, dict) else row
            if name is not None:
                names.append(name)
        return names

    @property
    def value(self):
        """A parsed copy of `raw_value`: a new dict with the same rows, each
        cell parsed per its column. `raw_value` is unchanged."""
        val = self.raw_value
        if not isinstance(val, dict):
            return val
        return {
            name: self._parse_row(row) if isinstance(row, dict) else row
            for name, row in val.items()
        }

    def _iter_rows(self):
        """A matrixdropdown's rows are the ones its schema declares, keyed by
        name: `quality[speed].rating`.

        The schema rather than the submitted value, so a row nobody answered
        still has its cells — a matrixdropdown shows every row it declares,
        answered or not.
        """
        return (
            (name, self.get_row_raw_value(name))
            for name in self.row_names
        )

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

    def value_spec(self):
        """An object keyed by row name, each row an object of cells."""
        row = self._row_spec()
        return {
            'type': 'object',
            'properties': {name: row for name in self.row_names},
            'additionalProperties': False,
        }
