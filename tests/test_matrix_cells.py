# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""A matrix's cells, as questions.

A column declares a `cellType`, which is a question type, so a cell is a
question of that type holding one value. Reading it that way is what gives a
cell the behaviour of its type — a dropdown's `value_text`, a boolean's
labels — where `get_cell_value()` only ever types the value by `inputType`.
"""

import unittest

from surveyjs.elements.dropdown import QuestionDropdown
from surveyjs.elements.text import QuestionText
from tests.utils import load_creator, load_form


class TestMatrixDynamicCells(unittest.TestCase):
    """`employeeList`: three rows of name (text) / role (dropdown) / salary."""

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['employeeList']

    def test_a_cell_is_a_question_of_its_column_cell_type(self):
        cell = self.q.get_cell(0, 'role')
        self.assertIsInstance(cell, QuestionDropdown)
        self.assertIsInstance(self.q.get_cell(0, 'name'), QuestionText)

    def test_a_cell_holds_its_own_value(self):
        self.assertEqual(self.q.get_cell(0, 'name').value, 'Bob Smith')
        self.assertEqual(self.q.get_cell(1, 'name').value, 'Jane Doe')
        self.assertEqual(self.q.get_cell(2, 'role').value, 'manager')

    def test_a_cell_behaves_like_its_type(self):
        """The point of the exercise: a dropdown cell resolves its choices."""
        self.assertEqual(self.q.get_cell(1, 'role').value_text, 'designer')

    def test_one_row_of_cells(self):
        cells = self.q.cells(1)
        self.assertEqual(list(cells), ['name', 'role', 'salary'])
        self.assertEqual(cells['salary'].value, '85000')

    def test_every_submitted_row_is_materialised(self):
        self.assertEqual(len(self.q.rows_cells), 3)
        self.assertEqual(list(self.q.rows_cells), [0, 1, 2])

    def test_no_such_row_or_column(self):
        self.assertEqual(self.q.cells(99), {})
        self.assertIsNone(self.q.get_cell(0, 'nosuchcolumn'))
        self.assertIsNone(self.q.get_cell(99, 'name'))

    # -- addressing ---------------------------------------------------------
    def test_a_cell_is_registered_by_path(self):
        """Never by name — a column name repeats in every row."""
        cell = self.form.get_element_by_path('employeeList[1].role')
        self.assertIs(cell, self.q.get_cell(1, 'role'))
        self.assertNotIn('role', self.form.questions)

    def test_a_cell_knows_where_its_value_lives(self):
        cell = self.q.get_cell(2, 'salary')
        self.assertEqual(cell.input_path, ['employeeList', 2, 'salary'])
        self.assertEqual(cell.input_path_str, 'employeeList[2].salary')
        self.assertEqual(cell.row_key, 2)

    def test_the_matrix_itself_is_unchanged(self):
        """The value-level API keeps reading the submission as submitted."""
        self.assertEqual(self.q.rows_data[0]['name'], 'Bob Smith')
        self.assertEqual(self.q.get_cell_value(0, 'name'), 'Bob Smith')
        self.assertEqual(self.q.get_row_value(0)['role'], 'developer')
        self.assertEqual(self.q.actual_row_count, 3)


class TestMatrixDropdownCells(unittest.TestCase):
    """`budgetMatrix`: rows named marketing / development, keyed by name."""

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['budgetMatrix']

    def test_rows_are_keyed_by_name(self):
        self.assertEqual(self.q.row_names, ['marketing', 'development'])
        self.assertEqual(list(self.q.rows_cells), ['marketing', 'development'])

    def test_a_cell_is_a_question_of_its_column_cell_type(self):
        self.assertIsInstance(self.q.get_cell('marketing', 'status'), QuestionDropdown)

    def test_a_cell_knows_where_its_value_lives(self):
        cell = self.q.get_cell('development', 'q1')
        self.assertEqual(cell.input_path, ['budgetMatrix', 'development', 'q1'])
        self.assertEqual(cell.input_path_str, 'budgetMatrix.development.q1')
        self.assertEqual(cell.row_key, 'development')

    def test_a_cell_is_registered_by_path(self):
        cell = self.form.get_element_by_path('budgetMatrix[marketing].status')
        self.assertIs(cell, self.q.get_cell('marketing', 'status'))

    def test_a_column_inherits_the_question_choices(self):
        """`budgetMatrix` declares choices for the columns that name none."""
        cell = self.q.get_cell('marketing', 'q1')
        self.assertEqual(cell.raw.get('choices'), ['low', 'medium', 'high'])


class TestMatrixCellsOnACreator(unittest.TestCase):
    """A Creator has no submission, so it has no rows to materialise."""

    def setUp(self):
        self.q = load_creator().questions['employeeList']

    def test_no_cells_without_data(self):
        self.assertEqual(self.q.rows_cells, {})
        self.assertIsNone(self.q.get_cell(0, 'name'))

    def test_columns_are_still_the_definition(self):
        self.assertEqual(self.q.column_names, ['name', 'role', 'salary'])
        self.assertEqual(self.q.get_column('role').cell_type, 'dropdown')

    def test_a_column_reads_as_the_element_its_cells_are(self):
        raw = self.q.get_column('role').cell_raw
        self.assertEqual(raw['type'], 'dropdown')
        self.assertEqual(raw['name'], 'role')
        self.assertEqual(raw['choices'], ['developer', 'designer', 'manager'])


if __name__ == '__main__':
    unittest.main()
