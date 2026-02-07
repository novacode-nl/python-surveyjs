# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the matrix question type."""

import unittest

from tests.utils import load_survey, load_form


class TestMatrixSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['qualityMatrix']

    def test_class_type(self):
        from surveyjs_data.questions.matrix import matrixQuestion
        self.assertIsInstance(self.q, matrixQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'matrix')

    def test_title(self):
        self.assertEqual(self.q.title, 'Rate the quality')

    def test_columns(self):
        self.assertEqual(len(self.q.columns), 4)

    def test_column_values(self):
        values = self.q.column_values
        val_names = [v['value'] for v in values]
        self.assertIn('poor', val_names)
        self.assertIn('excellent', val_names)

    def test_rows(self):
        self.assertEqual(len(self.q.rows), 3)

    def test_row_values(self):
        values = self.q.row_values
        val_names = [v['value'] for v in values]
        self.assertIn('product', val_names)
        self.assertIn('service', val_names)
        self.assertIn('support', val_names)

    def test_is_all_row_required(self):
        self.assertTrue(self.q.is_all_row_required)


class TestMatrixForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['qualityMatrix']

    def test_value_is_dict(self):
        self.assertIsInstance(self.q.value, dict)

    def test_get_row_value(self):
        self.assertEqual(self.q.get_row_value('product'), 'excellent')
        self.assertEqual(self.q.get_row_value('service'), 'good')
        self.assertEqual(self.q.get_row_value('support'), 'fair')

    def test_get_row_value_nonexistent(self):
        self.assertIsNone(self.q.get_row_value('nonexistent'))


if __name__ == '__main__':
    unittest.main()
