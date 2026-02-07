# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the matrixdynamic question type."""

import unittest

from tests.utils import load_survey, load_form


class TestMatrixDynamicSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['employeeList']

    def test_class_type(self):
        from surveyjs_data.questions.matrixdynamic import matrixdynamicQuestion
        self.assertIsInstance(self.q, matrixdynamicQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'matrixdynamic')

    def test_title(self):
        self.assertEqual(self.q.title, 'Employee List')

    def test_columns(self):
        self.assertEqual(len(self.q.columns), 3)

    def test_column_names(self):
        col_names = [c['name'] for c in self.q.columns]
        self.assertIn('name', col_names)
        self.assertIn('role', col_names)
        self.assertIn('salary', col_names)

    def test_row_count(self):
        self.assertEqual(self.q.row_count, 2)

    def test_min_row_count(self):
        self.assertEqual(self.q.min_row_count, 1)

    def test_max_row_count(self):
        self.assertEqual(self.q.max_row_count, 10)

    def test_cell_type(self):
        self.assertEqual(self.q.cell_type, 'text')


class TestMatrixDynamicForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['employeeList']

    def test_value_is_list(self):
        self.assertIsInstance(self.q.value, list)

    def test_rows_data(self):
        self.assertEqual(len(self.q.rows_data), 3)

    def test_actual_row_count(self):
        self.assertEqual(self.q.actual_row_count, 3)

    def test_get_cell_value(self):
        self.assertEqual(self.q.get_cell_value(0, 'name'), 'Bob Smith')
        self.assertEqual(self.q.get_cell_value(0, 'role'), 'developer')
        self.assertEqual(self.q.get_cell_value(1, 'name'), 'Jane Doe')
        self.assertEqual(self.q.get_cell_value(2, 'salary'), '110000')

    def test_get_cell_value_out_of_range(self):
        self.assertIsNone(self.q.get_cell_value(99, 'name'))


if __name__ == '__main__':
    unittest.main()
