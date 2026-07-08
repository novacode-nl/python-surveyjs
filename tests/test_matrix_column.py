# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for matrix columns and per-column `inputType` cell parsing.

`matrixdropdown` and `matrixdynamic` columns may declare a `cellType: text`
with an `inputType`, so each cell parses per its own column — the same rule as
a `multipletext` item, and a `text` question.
"""

import unittest
from datetime import date, datetime

from surveyjs import SurveyCreator, SurveyForm
from surveyjs.elements.column import MatrixColumn
from tests.utils import load_form

DYNAMIC_SCHEMA = {'elements': [
    {'type': 'matrixdynamic', 'name': 'md', 'cellType': 'text', 'columns': [
        {'name': 'when', 'cellType': 'text', 'inputType': 'date'},
        {'name': 'at', 'cellType': 'text', 'inputType': 'datetime-local'},
        {'name': 'amount', 'cellType': 'text', 'inputType': 'number'},
        {'name': 'role', 'cellType': 'dropdown', 'choices': ['dev', 'ops']},
        {'name': 'note'},
    ]},
]}

DYNAMIC_DATA = {'md': [
    {'when': '2024-03-15', 'at': '2024-03-15T13:45', 'amount': '42', 'role': 'dev', 'note': 'hi'},
    {'when': 'bad-date', 'at': '2025-01-02T08:00', 'amount': '4.2', 'role': 'ops', 'note': 'yo'},
]}

DROPDOWN_SCHEMA = {'elements': [
    {'type': 'matrixdropdown', 'name': 'mdd', 'cellType': 'text',
     'rows': ['r1', 'r2'], 'columns': [
         {'name': 'start', 'cellType': 'text', 'inputType': 'date'},
         {'name': 'status', 'cellType': 'dropdown', 'choices': ['ok']},
     ]},
]}

DROPDOWN_DATA = {'mdd': {'r1': {'start': '2024-07-08', 'status': 'ok'}}}


def make_form(schema, data):
    return SurveyForm(data, creator=SurveyCreator(schema))


class TestMatrixColumn(unittest.TestCase):

    def setUp(self):
        self.q = make_form(DYNAMIC_SCHEMA, DYNAMIC_DATA).questions['md']

    def test_columns_are_objects(self):
        self.assertEqual(len(self.q.columns), 5)
        for column in self.q.columns:
            self.assertIsInstance(column, MatrixColumn)

    def test_column_names(self):
        self.assertEqual(self.q.column_names, ['when', 'at', 'amount', 'role', 'note'])

    def test_column_count(self):
        self.assertEqual(self.q.column_count, 5)

    def test_get_column(self):
        self.assertEqual(self.q.get_column('when').name, 'when')

    def test_get_column_missing(self):
        self.assertIsNone(self.q.get_column('nope'))

    def test_input_type(self):
        self.assertEqual(self.q.get_column('when').input_type, 'date')
        self.assertEqual(self.q.get_column('amount').input_type, 'number')

    def test_non_text_cell_type_has_no_input_type(self):
        """A dropdown cell carries no inputType, so its values pass through."""
        self.assertEqual(self.q.get_column('role').input_type, '')

    def test_cell_type_defaults_to_the_questions(self):
        """The 'note' column declares no cellType; the question says 'text'."""
        self.assertEqual(self.q.get_column('note').cell_type, 'text')
        self.assertEqual(self.q.get_column('note').input_type, 'text')

    def test_title_falls_back_to_name(self):
        self.assertEqual(self.q.get_column('when').title, 'when')

    def test_choices_default_to_the_questions(self):
        self.assertEqual(self.q.get_column('role').choices, ['dev', 'ops'])
        self.assertEqual(self.q.get_column('when').choices, self.q.choices)

    def test_parse(self):
        self.assertEqual(self.q.get_column('when').parse('2024-03-15'), date(2024, 3, 15))

    def test_parse_unparseable(self):
        self.assertIsNone(self.q.get_column('when').parse('nope'))

    def test_repr_and_to_dict(self):
        column = self.q.get_column('when')
        self.assertEqual(repr(column), '<MatrixColumn name=when>')
        self.assertEqual(column.to_dict(), {
            'name': 'when', 'title': 'when', 'cellType': 'text', 'inputType': 'date',
        })


class TestMatrixdynamicCells(unittest.TestCase):

    def setUp(self):
        self.q = make_form(DYNAMIC_SCHEMA, DYNAMIC_DATA).questions['md']

    def test_cell_value_parses_per_column(self):
        self.assertEqual(self.q.get_cell_value(0, 'when'), date(2024, 3, 15))
        self.assertEqual(self.q.get_cell_value(0, 'at'), datetime(2024, 3, 15, 13, 45))
        self.assertEqual(self.q.get_cell_value(0, 'amount'), 42)
        self.assertEqual(self.q.get_cell_value(1, 'amount'), 4.2)

    def test_non_text_cell_passes_through(self):
        self.assertEqual(self.q.get_cell_value(0, 'role'), 'dev')
        self.assertEqual(self.q.get_cell_value(0, 'note'), 'hi')

    def test_cell_raw_value(self):
        self.assertEqual(self.q.get_cell_raw_value(0, 'when'), '2024-03-15')
        self.assertEqual(self.q.get_cell_raw_value(0, 'amount'), '42')

    def test_malformed_cell_yields_none_but_raw_survives(self):
        self.assertIsNone(self.q.get_cell_value(1, 'when'))
        self.assertEqual(self.q.get_cell_raw_value(1, 'when'), 'bad-date')

    def test_row_value_parses_every_cell(self):
        self.assertEqual(self.q.get_row_value(0), {
            'when': date(2024, 3, 15),
            'at': datetime(2024, 3, 15, 13, 45),
            'amount': 42,
            'role': 'dev',
            'note': 'hi',
        })

    def test_row_raw_value(self):
        self.assertEqual(self.q.get_row_raw_value(0), DYNAMIC_DATA['md'][0])

    def test_rows_data_stays_as_submitted(self):
        """rows_data normalises the container, it does not parse cells."""
        self.assertEqual(self.q.rows_data, DYNAMIC_DATA['md'])

    def test_question_value_is_the_unparsed_list(self):
        """The question declares no inputType; only its columns do."""
        self.assertEqual(self.q.value, self.q.raw_value)
        self.assertEqual(self.q.value, DYNAMIC_DATA['md'])

    def test_out_of_range_row(self):
        self.assertIsNone(self.q.get_cell_value(99, 'when'))
        self.assertEqual(self.q.get_row_value(99), {})
        self.assertEqual(self.q.get_row_raw_value(99), {})

    def test_negative_row_index_does_not_wrap(self):
        self.assertEqual(self.q.get_row_raw_value(-1), {})
        self.assertIsNone(self.q.get_cell_value(-1, 'when'))

    def test_unknown_column(self):
        self.assertIsNone(self.q.get_cell_value(0, 'nope'))
        self.assertIsNone(self.q.get_cell_raw_value(0, 'nope'))

    def test_no_data(self):
        q = make_form(DYNAMIC_SCHEMA, {}).questions['md']
        self.assertEqual(q.rows_data, [])
        self.assertEqual(q.get_row_value(0), {})
        self.assertIsNone(q.get_cell_value(0, 'when'))


class TestMatrixdropdownCells(unittest.TestCase):

    def setUp(self):
        self.q = make_form(DROPDOWN_SCHEMA, DROPDOWN_DATA).questions['mdd']

    def test_cell_value_parses_per_column(self):
        self.assertEqual(self.q.get_cell_value('r1', 'start'), date(2024, 7, 8))

    def test_non_text_cell_passes_through(self):
        self.assertEqual(self.q.get_cell_value('r1', 'status'), 'ok')

    def test_cell_raw_value(self):
        self.assertEqual(self.q.get_cell_raw_value('r1', 'start'), '2024-07-08')

    def test_row_value_parses_every_cell(self):
        self.assertEqual(self.q.get_row_value('r1'), {'start': date(2024, 7, 8), 'status': 'ok'})

    def test_row_raw_value(self):
        self.assertEqual(self.q.get_row_raw_value('r1'), {'start': '2024-07-08', 'status': 'ok'})

    def test_missing_row(self):
        self.assertEqual(self.q.get_row_value('r2'), {})
        self.assertEqual(self.q.get_row_raw_value('r2'), {})
        self.assertIsNone(self.q.get_cell_value('r2', 'start'))

    def test_unknown_row_and_column(self):
        self.assertIsNone(self.q.get_cell_value('nope', 'start'))
        self.assertIsNone(self.q.get_cell_value('r1', 'nope'))

    def test_question_value_is_the_unparsed_dict(self):
        self.assertEqual(self.q.value, self.q.raw_value)


class TestFixtureMatricesUnaffected(unittest.TestCase):
    """The fixture's matrices declare no cell inputType: values pass through."""

    def setUp(self):
        self.form = load_form()

    def test_matrixdynamic_cells_unchanged(self):
        q = self.form.questions['employeeList']
        self.assertEqual(q.get_cell_value(0, 'name'), 'Bob Smith')
        self.assertEqual(q.get_cell_value(2, 'salary'), '110000')

    def test_matrixdropdown_cells_unchanged(self):
        q = self.form.questions['budgetMatrix']
        self.assertEqual(q.get_cell_value('marketing', 'q1'), '10000')
        self.assertEqual(q.get_cell_value('development', 'status'), 'planned')

    def test_cell_value_equals_raw_without_input_type(self):
        q = self.form.questions['employeeList']
        for index in range(q.actual_row_count):
            for name in q.column_names:
                self.assertEqual(q.get_cell_value(index, name),
                                 q.get_cell_raw_value(index, name))


if __name__ == '__main__':
    unittest.main()
