# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the checkbox question type."""

import unittest

from tests.utils import load_survey, load_form


class TestCheckboxSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['hobbies']

    def test_class_type(self):
        from surveyjs_data.questions.checkbox import checkboxQuestion
        self.assertIsInstance(self.q, checkboxQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'checkbox')

    def test_title(self):
        self.assertEqual(self.q.title, 'Hobbies')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 5)

    def test_choices_values(self):
        values = self.q.choices_values
        self.assertEqual(len(values), 5)
        val_names = [v['value'] for v in values]
        self.assertIn('reading', val_names)
        self.assertIn('sports', val_names)

    def test_has_other(self):
        self.assertTrue(self.q.has_other)

    def test_has_none(self):
        self.assertTrue(self.q.has_none)

    def test_has_select_all(self):
        self.assertTrue(self.q.has_select_all)

    def test_max_selected_choices(self):
        self.assertEqual(self.q.max_selected_choices, 3)

    def test_min_selected_choices(self):
        self.assertEqual(self.q.min_selected_choices, 1)

    def test_col_count(self):
        self.assertEqual(self.q.col_count, 3)


class TestCheckboxForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['hobbies']

    def test_value_is_list(self):
        self.assertIsInstance(self.q.value, list)

    def test_value_contents(self):
        self.assertEqual(self.q.value, ['reading', 'music', 'travel'])

    def test_value_texts(self):
        texts = self.q.value_texts
        self.assertIn('Reading', texts)
        self.assertIn('Music', texts)
        self.assertIn('Travel', texts)

    def test_value_texts_count(self):
        self.assertEqual(len(self.q.value_texts), 3)


if __name__ == '__main__':
    unittest.main()
