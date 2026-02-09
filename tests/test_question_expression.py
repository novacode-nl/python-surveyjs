# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the expression question type."""

import unittest

from tests.utils import load_creator, load_form


class TestExpressionSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['fullName']

    def test_class_type(self):
        from surveyjs.questions.expression_q import expressionQuestion
        self.assertIsInstance(self.q, expressionQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'expression')

    def test_title(self):
        self.assertEqual(self.q.title, 'Full Name')

    def test_expression(self):
        self.assertEqual(self.q.expression, "{firstName} + ' Smith'")

    def test_display_style(self):
        self.assertEqual(self.q.display_style, 'none')


class TestExpressionForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['fullName']

    def test_value(self):
        self.assertEqual(self.q.value, 'Alice Smith')

    def test_to_number_returns_none_for_string(self):
        self.assertIsNone(self.q.to_number())


if __name__ == '__main__':
    unittest.main()
