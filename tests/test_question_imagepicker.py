# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the imagepicker question type."""

import unittest

from tests.utils import load_survey, load_form


class TestImagepickerSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['favoritePet']

    def test_class_type(self):
        from surveyjs_data.questions.imagepicker import imagepickerQuestion
        self.assertIsInstance(self.q, imagepickerQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'imagepicker')

    def test_title(self):
        self.assertEqual(self.q.title, 'Favorite Pet')

    def test_choices(self):
        self.assertEqual(len(self.q.choices), 3)

    def test_multi_select(self):
        self.assertFalse(self.q.multi_select)

    def test_show_label(self):
        self.assertTrue(self.q.show_label)

    def test_image_fit(self):
        self.assertEqual(self.q.image_fit, 'cover')

    def test_image_height(self):
        self.assertEqual(self.q.image_height, 150)

    def test_image_width(self):
        self.assertEqual(self.q.image_width, 200)

    def test_content_mode(self):
        self.assertEqual(self.q.content_mode, 'image')


class TestImagepickerForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['favoritePet']

    def test_value(self):
        self.assertEqual(self.q.value, 'cat')


if __name__ == '__main__':
    unittest.main()
