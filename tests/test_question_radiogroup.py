# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the radiogroup question type."""

import unittest

from surveyjs.elements.radiogroup import QuestionRadiogroup
from tests.utils import load_creator, load_form


class TestQuestionRadiogroup(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['favoriteColor']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionRadiogroup)

    def test_type(self):
        self.assertEqual(self.q.type, 'radiogroup')

    def test_title(self):
        self.assertEqual(self.q.title, 'Favorite Color')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 4)

    def test_choices_values(self):
        values = self.q.choices_values
        self.assertEqual(len(values), 4)
        self.assertEqual(values[0]['value'], 'red')
        self.assertEqual(values[0]['text'], 'Red')

    def test_has_other(self):
        self.assertTrue(self.q.has_other)

    def test_has_none(self):
        self.assertFalse(self.q.has_none)

    def test_choices_order(self):
        self.assertEqual(self.q.choices_order, 'random')

    def test_col_count(self):
        self.assertEqual(self.q.col_count, 2)

    def test_is_required(self):
        self.assertTrue(self.q.is_required)


class TestRadiogroupForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['favoriteColor']

    def test_value(self):
        self.assertEqual(self.q.value, 'blue')

    def test_value_text(self):
        self.assertEqual(self.q.value_text, 'Blue')


if __name__ == '__main__':
    unittest.main()
