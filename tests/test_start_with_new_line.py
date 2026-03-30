# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the text question type."""

import unittest

from tests.utils import load_creator, load_form


class TestCreatorStartWithNewLine(unittest.TestCase):

    def setUp(self):
        self.creator = load_creator()

    def test_start_with_new_line_default_true(self):
        """startWithNewLine defaults to True when not specified."""
        self.assertTrue(self.creator.questions['firstName'].start_with_new_line)

    def test_start_with_new_line_false(self):
        """startWithNewLine is False when explicitly set."""
        self.assertFalse(self.creator.questions['age'].start_with_new_line)
        self.assertFalse(self.creator.questions['birthDate'].start_with_new_line)

    def test_elements_on_same_line_returns_false_start_with_new_line(self):
        """elements_on_same_line returns sibling elements where startWithNewLine is False."""
        elements = self.creator.questions['firstName'].elements_on_same_line
        self.assertEqual(elements, [])
        elements_same_line = self.creator.questions['age'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertIn('age', names_same_line)
        self.assertIn('birthDate', names_same_line)

    def test_elements_on_same_line_excludes_default_start_with_new_line(self):
        """elements_on_same_line does not include elements where startWithNewLine defaults to True."""
        elements = self.creator.questions['firstName'].elements_on_same_line
        self.assertEqual(elements, [])
        elements_same_line = self.creator.questions['age'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertNotIn('firstName', names_same_line)
        self.assertNotIn('email', names_same_line)

    def test_elements_on_same_line_count(self):
        """elements_on_same_line returns exactly the elements with startWithNewLine False."""
        elements = self.creator.questions['age'].elements_on_same_line
        self.assertEqual(len(elements), 2)


class TestFormStartWithNewLine(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_start_with_new_line_default_true(self):
        """startWithNewLine defaults to True when not specified."""
        self.assertTrue(self.form.questions['firstName'].start_with_new_line)

    def test_start_with_new_line_false(self):
        """startWithNewLine is False when explicitly set."""
        self.assertFalse(self.form.questions['age'].start_with_new_line)

    def test_elements_on_same_line_returns_false_start_with_new_line(self):
        """elements_on_same_line returns sibling elements where startWithNewLine is False."""
        elements_same_line = self.form.questions['age'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertIn('age', names_same_line)
        self.assertIn('birthDate', names_same_line)

    def test_elements_on_same_line_excludes_default_start_with_new_line(self):
        """elements_on_same_line does not include elements where startWithNewLine defaults to True."""
        elements_same_line = self.form.questions['age'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertNotIn('firstName', names_same_line)
        self.assertNotIn('email', names_same_line)

    def test_elements_on_same_line_count(self):
        """elements_on_same_line returns exactly the elements with startWithNewLine False."""
        elements = self.form.questions['age'].elements_on_same_line
        self.assertEqual(len(elements), 2)

if __name__ == '__main__':
    unittest.main()
