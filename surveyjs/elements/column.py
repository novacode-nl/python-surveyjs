# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from collections import OrderedDict

from .inputtype import parse_boolean, parse_input_value


class MatrixColumn:
    """One column of a `matrixdropdown` or `matrixdynamic` question.

    Columns are not survey elements — they have no `type` and never appear in
    an owner's registries — but a column whose `cellType` is `text` may carry
    an `inputType`, so every cell in that column parses accordingly. A
    `boolean` cell parses to a Python bool, honouring the column's
    `valueTrue` / `valueFalse`.

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
        return self.question.translate(self.raw.get('title')) or self.question.translate(self.name)

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

    @property
    def cell_raw(self):
        """This column as the definition of the question one of its cells is.

        A column already reads like an element — a name, a title, choices, an
        `isRequired` — with its type spelled `cellType` and, where the column
        says nothing, taken from the question it belongs to. This is that
        element definition: what the matrix builds each of its cells from.
        """
        raw = dict(self.raw)
        raw['type'] = self.cell_type
        raw['name'] = self.name
        if self.input_type:
            raw['inputType'] = self.input_type
        if 'choices' not in raw and self.choices:
            raw['choices'] = self.choices
        return raw

    def parse(self, raw_cell_value):
        """Parse one raw cell value according to this column's `inputType`,
        or to a bool for a `boolean` cell (None if unrecognised)."""
        if self.cell_type == 'boolean':
            if raw_cell_value is None:
                return None
            try:
                return parse_boolean(
                    raw_cell_value,
                    self.raw.get('valueTrue', True),
                    self.raw.get('valueFalse', False))
            except ValueError:
                return None
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

    On a form, both also materialise their cells as *questions*: a column
    declares a `cellType`, which is a question type, so every cell is a
    question of that type holding that cell's value. See `cells()`.
    """

    def __init__(self, raw, survey, **kwargs):
        super().__init__(raw, survey, **kwargs)
        self._columns = [MatrixColumn(column, self) for column in self.raw.get('columns', [])]
        self._rows_cells = OrderedDict()

    @property
    def columns(self):
        """The column definitions, as `MatrixColumn` objects."""
        return self._columns

    # --- Cells as questions ------------------------------------------------
    #
    # A column is a definition, shared by every row; a cell is one value of
    # it. Reading a cell through `get_cell_value()` gives the value typed by
    # the column's `inputType` and nothing else — enough for a text or a
    # number, and not for a cell whose `cellType` is a question type with
    # behaviour of its own (a dropdown resolving what its choices mean, a
    # boolean knowing its own labels).
    #
    # So each cell is also built as a question of that `cellType`, through the
    # survey's element class mapping — the same mapping that decides every
    # other question's class, so an application that extends a type gets its
    # class in a matrix too. Cells are registered by path (`legs[0].country`)
    # like a dynamic panel's row children, never by name: a name repeats in
    # every row.
    #
    # Costs one element per cell on a form. A dynamic panel has always worked
    # this way; a matrix with hundreds of rows now pays the same.

    def load_data(self, data, is_form=False):
        """Load the matrix value, then materialise a question per cell.

        Only on the form path: a Creator has no submission data, so it has no
        rows — its columns are the whole story there.
        """
        super().load_data(data, is_form=is_form)
        if not is_form:
            return
        self._rows_cells = OrderedDict(
            (row_key, self._materialise_cells(row_key, row))
            for row_key, row in self._iter_rows()
        )

    def _iter_rows(self):
        """Yield `(row_key, row_data)` per row of the submitted value.

        Implemented by each matrix type: their rows are keyed differently — a
        dynamic matrix by position, a matrixdropdown by row name.
        """
        raise NotImplementedError

    def _materialise_cells(self, row_key, row):
        """Build one question per column for `row`, holding that cell's value."""
        cells = OrderedDict()
        for column in self._columns:
            if not column.name:
                continue
            element_obj = self.survey.get_element_object(column.cell_raw, language=self.language)
            if not element_obj:
                continue
            element_obj.row_key = row_key
            element_obj.load(
                element_owner=self.element_owner,
                parent=self,
                data=row if isinstance(row, dict) else {},
                is_form=True,
                # Column names repeat in every row: file these by path only.
                register_with_owner=False,
                register_with_parent=False,
            )
            cells[column.name] = element_obj
        return cells

    @property
    def nests_data(self):
        """A matrix's value holds one dict per row, so a cell's value is
        nested under the matrix's own name and its row's key."""
        return True

    @property
    def registrable_children(self):
        """A matrix's cells live in its rows, not in `elements`."""
        children = super().registrable_children
        for cells in self._rows_cells.values():
            children.extend(cells.values())
        return children

    @property
    def rows_cells(self):
        """`{row key: {column name: cell question}}` for every submitted row."""
        return self._rows_cells

    def cells(self, row_key):
        """The cell questions of one row, keyed by column name (empty when
        there is no such row)."""
        return self._rows_cells.get(row_key, OrderedDict())

    def get_cell(self, row_key, column_name):
        """One cell as a question, or None."""
        return self.cells(row_key).get(column_name)

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

    def _row_spec(self):
        """The value spec of one row: an object keyed by column name, each
        cell shaped as a question of its column's `cellType`. A computed
        (expression) column is left out: it holds no value to write."""
        properties = {}
        for column in self._columns:
            if not column.name:
                continue
            cell = self.survey.get_element_object(column.cell_raw, language=self.language)
            spec = cell.value_spec() if cell else {}
            if spec is not None:
                properties[column.name] = spec
        return {'type': 'object', 'properties': properties, 'additionalProperties': False}
