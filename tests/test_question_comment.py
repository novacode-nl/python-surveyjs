# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the comment question type."""

import unittest

from surveyjs.elements.comment import QuestionComment
from tests.utils import load_creator, load_form


class TestQuestionComment(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['bio']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionComment)

    def test_type(self):
        self.assertEqual(self.q.type, 'comment')

    def test_title(self):
        self.assertEqual(self.q.title, 'Biography')

    def test_description(self):
        self.assertEqual(self.q.description, 'Tell us about yourself')

    def test_max_length(self):
        self.assertEqual(self.q.max_length, 500)

    def test_rows(self):
        self.assertEqual(self.q.rows, 4)

    def test_auto_grow(self):
        self.assertTrue(self.q.auto_grow)

    def test_allow_resize(self):
        self.assertFalse(self.q.allow_resize)

    def test_is_input(self):
        self.assertTrue(self.q.is_input)


class TestCommentForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['bio']

    def test_value(self):
        self.assertIn('Software developer', self.q.value)

    def test_value_string(self):
        self.assertIsInstance(self.q.value, str)


if __name__ == '__main__':
    unittest.main()
