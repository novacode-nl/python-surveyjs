# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the multipletext question type."""

import unittest

from surveyjs.questions.multipletext import QuestionMultipletext
from tests.utils import load_creator, load_form


class TestQuestionMultipleText(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['address']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionMultipletext)

    def test_type(self):
        self.assertEqual(self.q.type, 'multipletext')

    def test_title(self):
        self.assertEqual(self.q.title, 'Address')

    def test_items(self):
        self.assertEqual(len(self.q.items), 4)

    def test_item_names(self):
        names = self.q.item_names
        self.assertIn('street', names)
        self.assertIn('city', names)
        self.assertIn('state', names)
        self.assertIn('zip', names)

    def test_item_count(self):
        self.assertEqual(self.q.item_count, 4)

    def test_col_count(self):
        self.assertEqual(self.q.col_count, 2)

    def test_get_item_title(self):
        self.assertEqual(self.q.get_item_title('street'), 'Street')
        self.assertEqual(self.q.get_item_title('city'), 'City')


class TestMultipleTextForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['address']

    def test_value_is_dict(self):
        self.assertIsInstance(self.q.value, dict)

    def test_get_item_value(self):
        self.assertEqual(self.q.get_item_value('street'), '123 Main Street')
        self.assertEqual(self.q.get_item_value('city'), 'Springfield')
        self.assertEqual(self.q.get_item_value('state'), 'IL')
        self.assertEqual(self.q.get_item_value('zip'), '62701')

    def test_get_item_value_nonexistent(self):
        self.assertIsNone(self.q.get_item_value('nonexistent'))


if __name__ == '__main__':
    unittest.main()
