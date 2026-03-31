# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the panel question type."""

import unittest

from surveyjs.elements.panel import QuestionPanel
from tests.utils import load_creator, load_form


class TestQuestionPanel(unittest.TestCase):

    def setUp(self):
        self.creator = load_creator()
        self.panel = self.creator.elements['contactPanel']

    def test_class_type(self):
        self.assertIsInstance(self.panel, QuestionPanel)

    def test_type(self):
        self.assertEqual(self.panel.type, 'panel')

    def test_panel_title(self):
        self.assertEqual(self.panel.title, 'Contact Information')

    def test_is_input(self):
        self.assertFalse(self.panel.is_input)

    def test_state(self):
        self.assertEqual(self.panel.state, 'expanded')

    def test_inner_indent(self):
        self.assertEqual(self.panel.inner_indent, 1)

    def test_elements(self):
        self.assertEqual(len(self.panel.elements), 2)

    def test_not_in_input_questions(self):
        self.assertNotIn('contactPanel', self.creator.questions)

    def test_in_questions(self):
        self.assertIn('contactPanel', self.creator.elements)

    def test_nested_questions_loaded(self):
        """Questions inside the panel should be loaded into the survey."""
        self.assertIn('phone', self.creator.questions)
        self.assertIn('website', self.creator.questions)


class TestPanelForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_not_in_input_questions(self):
        self.assertNotIn('contactPanel', self.form.questions)

    def test_nested_values_accessible(self):
        """Questions inside panel should get values from the flat form data."""
        self.assertEqual(self.form.get_value('phone'), '+1-555-0123')
        self.assertEqual(
            self.form.get_value('website'), 'https://alice.example.com'
        )


if __name__ == '__main__':
    unittest.main()
