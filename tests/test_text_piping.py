# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for SurveyJS text piping (`{panelIndex}`) in titles and descriptions."""

import unittest

from surveyjs import SurveyCreator, SurveyForm, interpolate_text


class TestInterpolateText(unittest.TestCase):

    def test_panel_index_is_one_based(self):
        self.assertEqual(interpolate_text('P #{panelIndex}', 0), 'P #1')
        self.assertEqual(interpolate_text('P #{panelIndex}', 1), 'P #2')

    def test_placeholder_left_alone_outside_a_row(self):
        self.assertEqual(interpolate_text('P #{panelIndex}'), 'P #{panelIndex}')

    def test_text_without_placeholder_passes_through(self):
        self.assertEqual(interpolate_text('plain', 0), 'plain')

    def test_falsy_text_passes_through(self):
        self.assertEqual(interpolate_text('', 0), '')
        self.assertIsNone(interpolate_text(None, 0))

    def test_other_pipes_are_untouched(self):
        self.assertEqual(interpolate_text('{row.year}', 0), '{row.year}')


class TestTitlePiping(unittest.TestCase):

    SCHEMA = {
        'elements': [
            {
                'type': 'paneldynamic',
                'name': 'passengers',
                'templateTitle': 'Passenger {panelIndex}',
                'templateElements': [
                    {'type': 'text', 'name': 'first',
                     'title': 'PASSENGER #{panelIndex} INFO',
                     'description': 'Details for #{panelIndex}'},
                    {'type': 'panel', 'name': 'grp', 'elements': [
                        {'type': 'text', 'name': 'deep', 'title': 'Deep #{panelIndex}'},
                    ]},
                ],
            },
            {'type': 'text', 'name': 'loose', 'title': 'Loose #{panelIndex}'},
        ],
    }
    DATA = {'passengers': [
        {'first': 'Bob', 'grp': {}},
        {'first': 'Finn', 'grp': {}},
    ]}

    def setUp(self):
        self.creator = SurveyCreator(self.SCHEMA)
        self.form = SurveyForm(self.DATA, creator=self.creator)
        self.panels = self.form.elements['passengers'].panels

    def test_row_child_title_is_piped_one_based(self):
        self.assertEqual(self.panels[0]['first'].title, 'PASSENGER #1 INFO')
        self.assertEqual(self.panels[1]['first'].title, 'PASSENGER #2 INFO')

    def test_label_alias_is_piped_too(self):
        self.assertEqual(self.panels[1]['first'].label, 'PASSENGER #2 INFO')

    def test_description_is_piped(self):
        self.assertEqual(self.panels[1]['first'].description, 'Details for #2')

    def test_nested_element_inherits_its_rows_index(self):
        """An element below a panel inside a row has no index of its own."""
        deep = self.panels[1]['grp'].elements['deep']
        self.assertIsNone(deep.panel_index)
        self.assertEqual(deep.title, 'Deep #2')

    def test_panel_instance_title_pipes_template_title(self):
        self.assertEqual(self.panels[0].title, 'Passenger 1')
        self.assertEqual(self.panels[1].title, 'Passenger 2')

    def test_template_child_keeps_placeholder(self):
        """The creator holds the template: no row, so no index to substitute."""
        template = self.creator.elements['passengers'].elements['first']
        self.assertEqual(template.title, 'PASSENGER #{panelIndex} INFO')

    def test_element_outside_a_dynamic_panel_keeps_placeholder(self):
        self.assertEqual(self.form.questions['loose'].title, 'Loose #{panelIndex}')


class TestTemplatePanel(unittest.TestCase):
    """`template_panel` renders a blank form's repeat as row 1."""

    def setUp(self):
        self.creator = SurveyCreator(TestTitlePiping.SCHEMA)
        self.paneldynamic = self.creator.elements['passengers']
        self.template_panel = self.paneldynamic.template_panel

    def test_is_row_one(self):
        self.assertEqual(self.template_panel.index, 0)
        self.assertEqual(self.template_panel.title, 'Passenger 1')

    def test_child_titles_are_piped_as_row_one(self):
        self.assertEqual(self.template_panel['first'].title, 'PASSENGER #1 INFO')

    def test_children_group_on_same_line(self):
        """Children carry a panel_instance, so sibling lookup works."""
        child = self.template_panel['first']
        self.assertIs(child.panel_instance, self.template_panel)
        self.assertEqual(child.panel_index, 0)

    def test_children_carry_no_submitted_values(self):
        self.assertIsNone(self.template_panel['first'].value)

    def test_built_once_and_cached(self):
        self.assertIs(self.paneldynamic.template_panel, self.template_panel)

    def test_creators_template_children_are_left_untouched(self):
        """Stamping the creator's own children would change their `path`."""
        template_child = self.paneldynamic.elements['first']
        self.assertIsNone(template_child.panel_index)
        self.assertIsNone(template_child.panel_instance)
        self.assertEqual(template_child.path_str, 'passengers.first')
        self.assertEqual(template_child.title, 'PASSENGER #{panelIndex} INFO')
        self.assertIn('passengers.first', self.creator.all_element_paths)

    def test_template_panel_children_are_distinct_objects(self):
        self.assertIsNot(self.template_panel['first'], self.paneldynamic.elements['first'])
        self.assertEqual(self.template_panel['first'].path_str, 'passengers[0].first')

    def test_a_form_row_is_unaffected(self):
        form = SurveyForm(TestTitlePiping.DATA, creator=self.creator)
        rows = form.elements['passengers'].panels
        self.assertEqual([r.index for r in rows], [0, 1])
        self.assertEqual(rows[1]['first'].title, 'PASSENGER #2 INFO')
        self.assertEqual(rows[1]['first'].value, 'Finn')


if __name__ == '__main__':
    unittest.main()
