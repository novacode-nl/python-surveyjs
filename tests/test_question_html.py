# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the html question type."""

import unittest

from surveyjs.elements.html import QuestionHtml
from tests.utils import load_creator, load_form


class TestQuestionHtml(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.elements['infoHtml']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionHtml)

    def test_type(self):
        self.assertEqual(self.q.type, 'html')

    def test_is_input(self):
        self.assertFalse(self.q.is_input)

    def test_html(self):
        self.assertIn('Thank you', self.q.html)
        self.assertIn('<p>', self.q.html)

    def test_not_in_input_questions(self):
        self.assertNotIn('infoHtml', self.survey.questions)

    def test_in_questions(self):
        self.assertIn('infoHtml', self.survey.elements)


class TestHtmlForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_not_in_input_questions(self):
        self.assertNotIn('infoHtml', self.form.questions)


if __name__ == '__main__':
    unittest.main()
