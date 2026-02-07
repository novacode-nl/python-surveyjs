# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the image question type."""

import unittest

from tests.utils import load_survey, load_form


class TestImageSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['thankYouImage']

    def test_class_type(self):
        from surveyjs.questions.image import imageQuestion
        self.assertIsInstance(self.q, imageQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'image')

    def test_is_input(self):
        self.assertFalse(self.q.is_input)

    def test_image_link(self):
        self.assertEqual(self.q.image_link, 'https://example.com/thankyou.png')

    def test_image_fit(self):
        self.assertEqual(self.q.image_fit, 'contain')

    def test_image_height(self):
        self.assertEqual(self.q.image_height, 300)

    def test_image_width(self):
        self.assertEqual(self.q.image_width, 400)

    def test_alt_text(self):
        self.assertEqual(self.q.alt_text, 'Thank you')

    def test_content_mode(self):
        self.assertEqual(self.q.content_mode, 'image')

    def test_not_in_input_questions(self):
        self.assertNotIn('thankYouImage', self.survey.input_questions)

    def test_in_questions(self):
        self.assertIn('thankYouImage', self.survey.questions)


class TestImageForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_not_in_input_questions(self):
        self.assertNotIn('thankYouImage', self.form.input_questions)


if __name__ == '__main__':
    unittest.main()
