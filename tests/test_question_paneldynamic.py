# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the paneldynamic question type."""

import unittest

from tests.utils import load_creator, load_form


class TestPanelDynamicSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['education']

    def test_class_type(self):
        from surveyjs.questions.paneldynamic import paneldynamicQuestion
        self.assertIsInstance(self.q, paneldynamicQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'paneldynamic')

    def test_title(self):
        self.assertEqual(self.q.title, 'Education History')

    def test_template_elements(self):
        self.assertEqual(len(self.q.template_elements), 3)

    def test_panel_count(self):
        self.assertEqual(self.q.panel_count, 1)

    def test_min_panel_count(self):
        self.assertEqual(self.q.min_panel_count, 0)

    def test_max_panel_count(self):
        self.assertEqual(self.q.max_panel_count, 5)

    def test_panel_add_text(self):
        self.assertEqual(self.q.panel_add_text, 'Add Education')

    def test_panel_remove_text(self):
        self.assertEqual(self.q.panel_remove_text, 'Remove')

    def test_allow_add_panel(self):
        self.assertTrue(self.q.allow_add_panel)

    def test_allow_remove_panel(self):
        self.assertTrue(self.q.allow_remove_panel)

    def test_template_title(self):
        self.assertEqual(self.q.template_title, 'Education #{panelIndex}')

    def test_is_input(self):
        """paneldynamic is an input element (its value is a list)."""
        self.assertTrue(self.q.is_input)


class TestPanelDynamicForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['education']

    def test_value_is_list(self):
        self.assertIsInstance(self.q.value, list)

    def test_panels_data(self):
        data = self.q.panels_data
        self.assertEqual(len(data), 2)

    def test_actual_panel_count(self):
        self.assertEqual(self.q.actual_panel_count, 2)

    def test_get_panel_value(self):
        self.assertEqual(self.q.get_panel_value(0, 'institution'), 'MIT')
        self.assertEqual(
            self.q.get_panel_value(0, 'degree'), 'BSc Computer Science'
        )
        self.assertEqual(self.q.get_panel_value(0, 'year'), 2015)

    def test_get_panel_value_second(self):
        self.assertEqual(self.q.get_panel_value(1, 'institution'), 'Stanford')
        self.assertEqual(self.q.get_panel_value(1, 'degree'), 'MSc AI')
        self.assertEqual(self.q.get_panel_value(1, 'year'), 2017)

    def test_get_panel_value_out_of_range(self):
        self.assertIsNone(self.q.get_panel_value(99, 'institution'))

    def test_get_panel_value_nonexistent_field(self):
        self.assertIsNone(self.q.get_panel_value(0, 'nonexistent'))


if __name__ == '__main__':
    unittest.main()
