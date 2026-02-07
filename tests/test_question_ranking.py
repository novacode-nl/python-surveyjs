# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the ranking question type."""

import unittest

from tests.utils import load_survey, load_form


class TestRankingSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['priorityItems']

    def test_class_type(self):
        from surveyjs_data.questions.ranking import rankingQuestion
        self.assertIsInstance(self.q, rankingQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'ranking')

    def test_title(self):
        self.assertEqual(self.q.title, 'Prioritize Items')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 4)

    def test_choices_values(self):
        values = self.q.choices_values
        val_names = [v['value'] for v in values]
        self.assertIn('price', val_names)
        self.assertIn('quality', val_names)
        self.assertIn('speed', val_names)
        self.assertIn('support', val_names)

    def test_long_tap(self):
        self.assertTrue(self.q.long_tap)

    def test_select_to_rank_enabled(self):
        self.assertFalse(self.q.select_to_rank_enabled)


class TestRankingForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['priorityItems']

    def test_value_is_list(self):
        self.assertIsInstance(self.q.value, list)

    def test_value_contents(self):
        self.assertEqual(
            self.q.value, ['quality', 'price', 'support', 'speed']
        )

    def test_value_order(self):
        """First item should be highest priority."""
        self.assertEqual(self.q.value[0], 'quality')
        self.assertEqual(self.q.value[-1], 'speed')


if __name__ == '__main__':
    unittest.main()
