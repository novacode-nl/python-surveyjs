# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the html question type."""

import unittest

from tests.utils import load_creator, load_form


class TestHtmlSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['infoHtml']

    def test_class_type(self):
        from surveyjs.questions.html import htmlQuestion
        self.assertIsInstance(self.q, htmlQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'html')

    def test_is_input(self):
        self.assertFalse(self.q.is_input)

    def test_html(self):
        self.assertIn('Thank you', self.q.html)
        self.assertIn('<p>', self.q.html)

    def test_not_in_input_questions(self):
        self.assertNotIn('infoHtml', self.survey.input_questions)

    def test_in_questions(self):
        self.assertIn('infoHtml', self.survey.questions)


class TestHtmlForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_not_in_input_questions(self):
        self.assertNotIn('infoHtml', self.form.input_questions)


if __name__ == '__main__':
    unittest.main()
