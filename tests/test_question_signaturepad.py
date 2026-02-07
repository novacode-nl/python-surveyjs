# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the signaturepad question type."""

import unittest

from tests.utils import load_survey, load_form


class TestSignaturepadSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['signature']

    def test_class_type(self):
        from surveyjs_data.questions.signaturepad import signaturepadQuestion
        self.assertIsInstance(self.q, signaturepadQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'signaturepad')

    def test_title(self):
        self.assertEqual(self.q.title, 'Your Signature')

    def test_signature_width(self):
        self.assertEqual(self.q.signature_width, 500)

    def test_signature_height(self):
        self.assertEqual(self.q.signature_height, 200)

    def test_pen_color(self):
        self.assertEqual(self.q.pen_color, '#000000')

    def test_background_color(self):
        self.assertEqual(self.q.background_color, '#ffffff')

    def test_data_format(self):
        self.assertEqual(self.q.data_format, 'png')

    def test_allow_clear(self):
        self.assertTrue(self.q.allow_clear)


class TestSignaturepadForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['signature']

    def test_value_is_base64(self):
        self.assertTrue(self.q.value.startswith('data:image/png;base64,'))

    def test_is_base64(self):
        self.assertTrue(self.q.is_base64)


if __name__ == '__main__':
    unittest.main()
