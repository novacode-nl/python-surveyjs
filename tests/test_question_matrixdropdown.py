# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the matrixdropdown question type."""

import unittest

from surveyjs.questions.matrixdropdown import QuestionMatrixdropdown
from tests.utils import load_creator, load_form


class TestQuestionMatrixdropdown(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['budgetMatrix']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionMatrixdropdown)

    def test_type(self):
        self.assertEqual(self.q.type, 'matrixdropdown')

    def test_title(self):
        self.assertEqual(self.q.title, 'Annual Budget')

    def test_columns(self):
        self.assertEqual(len(self.q.columns), 3)

    def test_column_names(self):
        col_names = [c['name'] for c in self.q.columns]
        self.assertIn('q1', col_names)
        self.assertIn('q2', col_names)
        self.assertIn('status', col_names)

    def test_rows(self):
        self.assertEqual(len(self.q.rows), 2)

    def test_cell_type(self):
        self.assertEqual(self.q.cell_type, 'text')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 3)


class TestMatrixDropdownForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['budgetMatrix']

    def test_value_is_dict(self):
        self.assertIsInstance(self.q.value, dict)

    def test_get_row_value(self):
        row = self.q.get_row_value('marketing')
        self.assertIsInstance(row, dict)
        self.assertEqual(row['q1'], '10000')
        self.assertEqual(row['status'], 'approved')

    def test_get_cell_value(self):
        self.assertEqual(self.q.get_cell_value('marketing', 'q1'), '10000')
        self.assertEqual(self.q.get_cell_value('development', 'q2'), '55000')
        self.assertEqual(self.q.get_cell_value('development', 'status'), 'planned')

    def test_get_cell_value_nonexistent(self):
        self.assertIsNone(self.q.get_cell_value('marketing', 'nonexistent'))
        self.assertIsNone(self.q.get_cell_value('nonexistent', 'q1'))


if __name__ == '__main__':
    unittest.main()
