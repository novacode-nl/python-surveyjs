# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the text question type."""

import unittest

from surveyjs import SurveyCreator, SurveyForm
from tests.utils import load_creator, load_form


class TestCreatorStartWithNewLine(unittest.TestCase):

    def setUp(self):
        self.creator = load_creator()

    def test_start_with_new_line_default_true(self):
        """startWithNewLine defaults to True when not specified."""
        self.assertTrue(self.creator.questions['firstName'].start_with_new_line)
        self.assertTrue(self.creator.questions['birthDate'].start_with_new_line)

    def test_start_with_new_line_false(self):
        """startWithNewLine is False when explicitly set."""
        self.assertFalse(self.creator.questions['lastName'].start_with_new_line)
        self.assertFalse(self.creator.questions['age'].start_with_new_line)

    def test_elements_on_same_line_returns_false_start_with_new_line(self):
        """elements_on_same_line returns sibling elements where startWithNewLine is False."""
        elements_same_line = self.creator.questions['firstName'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('firstName', names_same_line)
        self.assertIn('lastName', names_same_line)

        elements_same_line = self.creator.questions['lastName'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('firstName', names_same_line)
        self.assertIn('lastName', names_same_line)

        elements_same_line = self.creator.questions['birthDate'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('birthDate', names_same_line)
        self.assertIn('age', names_same_line)

        elements_same_line = self.creator.questions['age'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('birthDate', names_same_line)
        self.assertIn('age', names_same_line)

    def test_elements_on_same_line_excludes_default_start_with_new_line(self):
        """elements_on_same_line does not include elements where startWithNewLine defaults to True."""
        elements_same_line = self.creator.questions['email'].elements_on_same_line
        self.assertEqual(elements_same_line, [])
        elements_same_line = self.creator.questions['appointmentTime'].elements_on_same_line
        self.assertEqual(elements_same_line, [])
        names_same_line = [el.name for el in elements_same_line]
        self.assertNotIn('firstName', names_same_line)
        self.assertNotIn('lastName', names_same_line)
        self.assertNotIn('birthDate', names_same_line)
        self.assertNotIn('age', names_same_line)
        self.assertNotIn('email', names_same_line)


class TestFormStartWithNewLine(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_start_with_new_line_default_true(self):
        """startWithNewLine defaults to True when not specified."""
        self.assertTrue(self.form.questions['firstName'].start_with_new_line)
        self.assertTrue(self.form.questions['birthDate'].start_with_new_line)

    def test_start_with_new_line_false(self):
        """startWithNewLine is False when explicitly set."""
        self.assertFalse(self.form.questions['lastName'].start_with_new_line)
        self.assertFalse(self.form.questions['age'].start_with_new_line)

    def test_elements_on_same_line_returns_false_start_with_new_line(self):
        """elements_on_same_line returns sibling elements where startWithNewLine is False."""
        elements_same_line = self.form.questions['firstName'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('firstName', names_same_line)
        self.assertIn('lastName', names_same_line)

        elements_same_line = self.form.questions['lastName'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('firstName', names_same_line)
        self.assertIn('lastName', names_same_line)

        elements_same_line = self.form.questions['birthDate'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('birthDate', names_same_line)
        self.assertIn('age', names_same_line)

        elements_same_line = self.form.questions['age'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(len(elements_same_line), 2)
        self.assertIn('birthDate', names_same_line)
        self.assertIn('age', names_same_line)

    def test_elements_on_same_line_excludes_default_start_with_new_line(self):
        """elements_on_same_line does not include elements where startWithNewLine defaults to True."""
        elements_same_line = self.form.questions['email'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertNotIn('firstName', names_same_line)
        self.assertNotIn('lastName', names_same_line)
        self.assertNotIn('birthDate', names_same_line)
        self.assertNotIn('age', names_same_line)
        self.assertNotIn('email', names_same_line)


class TestNestedStartWithNewLine(unittest.TestCase):
    """elements_on_same_line must scope to the element's siblings.

    For nested elements (a panel's children) siblings come from the parent
    panel, not the top-level Survey/Form. The panel's children are absent from
    the owner's `elements`, so the property must resolve them via `parent`."""

    def setUp(self):
        schema = {
            'elements': [
                {
                    'type': 'panel',
                    'name': 'addressPanel',
                    'elements': [
                        {'type': 'text', 'name': 'city'},
                        {'type': 'text', 'name': 'zip', 'startWithNewLine': False},
                        {'type': 'text', 'name': 'country'},
                    ],
                },
            ],
        }
        self.creator = SurveyCreator(schema)

    def test_nested_elements_on_same_line(self):
        """A panel child groups with its panel siblings, not top-level elements."""
        elements_same_line = self.creator.questions['city'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(names_same_line, ['city', 'zip'])

        elements_same_line = self.creator.questions['zip'].elements_on_same_line
        names_same_line = [el.name for el in elements_same_line]
        self.assertEqual(names_same_line, ['city', 'zip'])

    def test_nested_default_start_with_new_line_alone(self):
        """A panel child that starts a new line is alone on its line."""
        self.assertEqual(
            self.creator.questions['country'].elements_on_same_line, []
        )


class TestPanelInstanceStartWithNewLine(unittest.TestCase):
    """A materialised paneldynamic row child groups with its own row.

    Its `parent` is the paneldynamic, whose `elements` holds the *template*
    children rather than this row's, so siblings must come from the
    `PanelInstance`. Resolving them through the parent raised ValueError.
    """

    SCHEMA = {
        'elements': [
            {
                'type': 'paneldynamic',
                'name': 'passengers',
                'templateElements': [
                    {'type': 'text', 'name': 'first'},
                    {'type': 'text', 'name': 'last', 'startWithNewLine': False},
                    {'type': 'text', 'name': 'note'},
                ],
            },
        ],
    }
    DATA = {'passengers': [
        {'first': 'Bob', 'last': 'Leers', 'note': 'a'},
        {'first': 'Finn', 'last': 'Leers', 'note': 'b'},
    ]}

    def setUp(self):
        self.creator = SurveyCreator(self.SCHEMA)
        self.form = SurveyForm(self.DATA, creator=self.creator)
        self.panels = self.form.elements['passengers'].panels

    def test_two_rows_materialised(self):
        self.assertEqual(len(self.panels), 2)

    def test_row_child_groups_with_its_row(self):
        """Does not raise, and groups on startWithNewLine within the row."""
        for row in self.panels:
            for name in ('first', 'last'):
                group = row[name].elements_on_same_line
                self.assertEqual([el.name for el in group], ['first', 'last'])

    def test_group_holds_this_rows_elements_not_another_rows(self):
        row0, row1 = self.panels
        group = row1['first'].elements_on_same_line
        self.assertIs(group[0], row1['first'])
        self.assertIs(group[1], row1['last'])
        self.assertIsNot(group[0], row0['first'])

    def test_row_child_alone_on_its_line(self):
        for row in self.panels:
            self.assertEqual(row['note'].elements_on_same_line, [])

    def test_panel_instance_back_reference(self):
        for index, row in enumerate(self.panels):
            for element in row:
                self.assertIs(element.panel_instance, row)
                self.assertEqual(element.panel_index, index)

    def test_non_repeating_elements_have_no_panel_instance(self):
        """The paneldynamic itself, and the creator's template children."""
        self.assertIsNone(self.form.elements['passengers'].panel_instance)
        for template_child in self.creator.elements['passengers'].elements.values():
            self.assertIsNone(template_child.panel_instance)

    def test_template_children_still_group_on_the_creator(self):
        """The creator keeps the template children, so they group via parent."""
        template = self.creator.elements['passengers'].elements
        group = template['last'].elements_on_same_line
        self.assertEqual([el.name for el in group], ['first', 'last'])


if __name__ == '__main__':
    unittest.main()
