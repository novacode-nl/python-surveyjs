# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the buttongroup question type."""

import unittest

from surveyjs.elements.buttongroup import QuestionButtongroup
from tests.utils import load_creator, load_form


class TestQuestionButtongroup(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['tShirtSize']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionButtongroup)

    def test_type(self):
        self.assertEqual(self.q.type, 'buttongroup')

    def test_title(self):
        self.assertEqual(self.q.title, 'T-Shirt Size')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 4)

    def test_choices_values(self):
        values = self.q.choices_values
        self.assertEqual(len(values), 4)
        self.assertEqual(values[0]['value'], 's')
        self.assertEqual(values[0]['text'], 'Small')

    def test_choice_icon_defaults(self):
        small = self.q.choices_values[0]
        self.assertIsNone(small['icon_name'])
        self.assertEqual(small['icon_size'], 24)
        self.assertTrue(small['show_caption'])

    def test_choice_icon_properties(self):
        medium = self.q.choices_values[1]
        self.assertEqual(medium['icon_name'], 'icon-medium')
        self.assertEqual(medium['icon_size'], 32)

    def test_choice_show_caption(self):
        large = self.q.choices_values[2]
        self.assertFalse(large['show_caption'])

    def test_allow_clear(self):
        self.assertFalse(self.q.allow_clear)

    def test_col_count(self):
        self.assertEqual(self.q.col_count, 4)

    def test_is_required(self):
        self.assertTrue(self.q.is_required)


class TestButtongroupForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['tShirtSize']

    def test_value(self):
        self.assertEqual(self.q.value, 'm')

    def test_value_text(self):
        self.assertEqual(self.q.value_text, 'Medium')


if __name__ == '__main__':
    unittest.main()
