# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the boolean question type."""

import unittest

from surveyjs.elements.boolean import QuestionBoolean
from tests.utils import load_creator, load_form


class TestQuestionBoolean(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['agreeTerms']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionBoolean)

    def test_type(self):
        self.assertEqual(self.q.type, 'boolean')

    def test_title(self):
        self.assertEqual(self.q.title, 'I agree to the Terms of Service')

    def test_label_true(self):
        self.assertEqual(self.q.label_true, 'Yes')

    def test_label_false(self):
        self.assertEqual(self.q.label_false, 'No')

    def test_value_true(self):
        self.assertEqual(self.q.value_true, 'agreed')

    def test_value_false(self):
        self.assertEqual(self.q.value_false, 'declined')

    def test_render_as(self):
        self.assertEqual(self.q.render_as, 'checkbox')


class TestBooleanForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['agreeTerms']

    def test_value(self):
        self.assertEqual(self.q.value, 'agreed')

    def test_to_bool_custom_true(self):
        self.assertTrue(self.q.to_bool())


if __name__ == '__main__':
    unittest.main()
