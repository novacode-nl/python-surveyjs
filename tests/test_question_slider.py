# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the slider question type."""

import unittest

from surveyjs.elements.slider import QuestionSlider
from tests.utils import load_creator, load_form


class TestQuestionSlider(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['volume']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionSlider)

    def test_type(self):
        self.assertEqual(self.q.type, 'slider')

    def test_title(self):
        self.assertEqual(self.q.title, 'Volume')

    def test_slider_type(self):
        self.assertEqual(self.q.slider_type, 'single')

    def test_is_range(self):
        self.assertFalse(self.q.is_range)

    def test_min_max_step(self):
        self.assertEqual(self.q.min, 0)
        self.assertEqual(self.q.max, 100)
        self.assertEqual(self.q.step, 5)

    def test_show_labels(self):
        self.assertTrue(self.q.show_labels)

    def test_tooltip_visibility(self):
        self.assertEqual(self.q.tooltip_visibility, 'always')

    def test_allow_clear(self):
        self.assertTrue(self.q.allow_clear)


class TestQuestionRangeSlider(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['priceRange']

    def test_slider_type(self):
        self.assertEqual(self.q.slider_type, 'range')

    def test_is_range(self):
        self.assertTrue(self.q.is_range)

    def test_allow_swap(self):
        self.assertFalse(self.q.allow_swap)

    def test_range_length(self):
        self.assertEqual(self.q.min_range_length, 50)
        self.assertEqual(self.q.max_range_length, 500)


class TestSliderForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.single = self.form.questions['volume']
        self.range_q = self.form.questions['priceRange']

    def test_single_value(self):
        self.assertEqual(self.single.value, 45)

    def test_single_to_number(self):
        self.assertEqual(self.single.to_number(), 45)

    def test_single_to_range(self):
        self.assertEqual(self.single.to_range(), [45, 45])

    def test_range_value(self):
        self.assertEqual(self.range_q.value, [100, 600])

    def test_range_to_range(self):
        self.assertEqual(self.range_q.to_range(), [100, 600])

    def test_range_to_number_returns_lower_bound(self):
        self.assertEqual(self.range_q.to_number(), 100)


if __name__ == '__main__':
    unittest.main()
