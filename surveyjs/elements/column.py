# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .inputtype import parse_input_value


class MatrixColumn:
    """One column of a `matrixdropdown` or `matrixdynamic` question.

    Columns are not survey elements — they have no `type` and never appear in
    an owner's registries — but a column whose `cellType` is `text` may carry
    an `inputType`, so every cell in that column parses accordingly.

    A column has no value of its own: its cells live in the question's rows.
    Use `parse(raw_cell_value)` to type one, or the question's
    `get_cell_value()` / `get_row_value()`, which do it for you.
    """

    def __init__(self, raw, question):
        self.raw = raw
        self.question = question

    @property
    def name(self):
        return self.raw.get('name', '')

    @property
    def title(self):
        """The column's display title, falling back to its name."""
        return self.raw.get('title') or self.name

    @property
    def cell_type(self):
        """This column's cell type, defaulting to the question's `cellType`."""
        return self.raw.get('cellType') or self.question.cell_type

    @property
    def input_type(self):
        """The `inputType` of this column's cells.

        Only a `text` cell carries one; other cell types (dropdown, checkbox,
        boolean, …) yield '' and so parse to themselves."""
        default = 'text' if self.cell_type == 'text' else ''
        return self.raw.get('inputType', default)

    @property
    def choices(self):
        """This column's choices, defaulting to the question's `choices`."""
        return self.raw.get('choices', self.question.choices)

    @property
    def is_required(self):
        return self.raw.get('isRequired', False)

    def parse(self, raw_cell_value):
        """Parse one raw cell value according to this column's `inputType`."""
        return parse_input_value(self.input_type, raw_cell_value)

    def __repr__(self):
        """`cell_type` is always meaningful, so it is always shown. Only a
        text cell has an `inputType`; append it when there is one rather than
        print an empty field."""
        if self.input_type:
            return '<MatrixColumn name=%s cell_type=%s input_type=%s>' % (
                self.name, self.cell_type, self.input_type)
        return '<MatrixColumn name=%s cell_type=%s>' % (self.name, self.cell_type)

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'cellType': self.cell_type,
            'inputType': self.input_type,
        }


class MatrixColumnsMixin:
    """Shared column handling for `matrixdropdown` and `matrixdynamic`.

    Both expose `columns` as `MatrixColumn` objects and parse their cells per
    the owning column's `inputType`.
    """

    def __init__(self, raw, survey, **kwargs):
        super().__init__(raw, survey, **kwargs)
        self._columns = [MatrixColumn(column, self) for column in self.raw.get('columns', [])]

    @property
    def columns(self):
        """The column definitions, as `MatrixColumn` objects."""
        return self._columns

    @property
    def column_names(self):
        return [column.name for column in self._columns]

    @property
    def column_count(self):
        return len(self._columns)

    def get_column(self, column_name):
        """Get a column by name, or None."""
        for column in self._columns:
            if column.name == column_name:
                return column
        return None

    def _parse_cell(self, column_name, raw_cell_value):
        """Parse a raw cell value per its column, or pass it through if the
        column is unknown."""
        column = self.get_column(column_name)
        if column is None:
            return raw_cell_value
        return column.parse(raw_cell_value)

    def _parse_row(self, raw_row):
        """Parse every cell of a raw row dict, per its own column."""
        if not isinstance(raw_row, dict):
            return {}
        return {name: self._parse_cell(name, value) for name, value in raw_row.items()}
