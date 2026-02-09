# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the rating question type."""

import unittest

from tests.utils import load_creator, load_form


class TestRatingSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['satisfaction']

    def test_class_type(self):
        from surveyjs.questions.rating import ratingQuestion
        self.assertIsInstance(self.q, ratingQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'rating')

    def test_title(self):
        self.assertEqual(self.q.title, 'Overall Satisfaction')

    def test_rate_min(self):
        self.assertEqual(self.q.rate_min, 1)

    def test_rate_max(self):
        self.assertEqual(self.q.rate_max, 10)

    def test_rate_step(self):
        self.assertEqual(self.q.rate_step, 1)

    def test_min_rate_description(self):
        self.assertEqual(self.q.min_rate_description, 'Very Bad')

    def test_max_rate_description(self):
        self.assertEqual(self.q.max_rate_description, 'Excellent')

    def test_display_mode(self):
        self.assertEqual(self.q.display_mode, 'buttons')

    def test_rate_type(self):
        self.assertEqual(self.q.rate_type, 'stars')


class TestRatingForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['satisfaction']

    def test_value(self):
        self.assertEqual(self.q.value, 8)

    def test_to_number(self):
        self.assertEqual(self.q.to_number(), 8)


if __name__ == '__main__':
    unittest.main()
