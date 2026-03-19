# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the tagbox question type."""

import unittest

from surveyjs.elements.tagbox import QuestionTagbox
from tests.utils import load_creator, load_form


class TestQuestionTagbox(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['skills']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionTagbox)

    def test_type(self):
        self.assertEqual(self.q.type, 'tagbox')

    def test_title(self):
        self.assertEqual(self.q.title, 'Skills')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 5)

    def test_choices_values(self):
        values = self.q.choices_values
        val_names = [v['value'] for v in values]
        self.assertIn('python', val_names)
        self.assertIn('javascript', val_names)

    def test_has_other(self):
        self.assertTrue(self.q.has_other)

    def test_search_enabled(self):
        self.assertTrue(self.q.search_enabled)

    def test_max_selected_choices(self):
        self.assertEqual(self.q.max_selected_choices, 4)


class TestTagboxForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['skills']

    def test_value_is_list(self):
        self.assertIsInstance(self.q.value, list)

    def test_value_contents(self):
        self.assertEqual(self.q.value, ['python', 'javascript', 'go'])

    def test_value_texts(self):
        texts = self.q.value_texts
        self.assertIn('Python', texts)
        self.assertIn('JavaScript', texts)
        self.assertIn('Go', texts)

    def test_value_texts_count(self):
        self.assertEqual(len(self.q.value_texts), 3)


if __name__ == '__main__':
    unittest.main()
