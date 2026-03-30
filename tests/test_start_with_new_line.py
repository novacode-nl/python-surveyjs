# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the text question type."""

import unittest

from tests.utils import load_creator, load_form


class TestCreatorStartWithNewLine(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()

    def test_start_with_new_line_default_true(self):
        """startWithNewLine defaults to True when not specified."""
        self.assertTrue(self.survey.questions['firstName'].start_with_new_line)

    def test_start_with_new_line_false(self):
        """startWithNewLine is False when explicitly set."""
        self.assertFalse(self.survey.questions['age'].start_with_new_line)
        self.assertFalse(self.survey.questions['birthDate'].start_with_new_line)


class TestFormStartWithNewLine(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_start_with_new_line_default_true(self):
        """startWithNewLine defaults to True when not specified."""
        self.assertTrue(self.form.questions['firstName'].start_with_new_line)

    def test_start_with_new_line_false(self):
        """startWithNewLine is False when explicitly set."""
        self.assertFalse(self.form.questions['age'].start_with_new_line)

if __name__ == '__main__':
    unittest.main()
