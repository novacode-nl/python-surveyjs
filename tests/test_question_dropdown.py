# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the dropdown question type."""

import unittest

from surveyjs.elements.dropdown import QuestionDropdown
from tests.utils import load_creator, load_form


class TestQuestionDropdown(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['country']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionDropdown)

    def test_type(self):
        self.assertEqual(self.q.type, 'dropdown')

    def test_title(self):
        self.assertEqual(self.q.title, 'Country')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 4)

    def test_choices_values(self):
        values = self.q.choices_values
        val_names = [v['value'] for v in values]
        self.assertIn('us', val_names)
        self.assertIn('uk', val_names)

    def test_has_other(self):
        self.assertFalse(self.q.has_other)

    def test_allow_clear(self):
        self.assertTrue(self.q.allow_clear)

    def test_search_enabled(self):
        self.assertTrue(self.q.search_enabled)


class TestDropdownForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['country']

    def test_value(self):
        self.assertEqual(self.q.value, 'us')

    def test_value_text(self):
        self.assertEqual(self.q.value_text, 'United States')


if __name__ == '__main__':
    unittest.main()
