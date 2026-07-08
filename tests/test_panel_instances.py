# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for materialised paneldynamic panel instances.

A SurveyCreator holds a dynamic panel's *template* children; a SurveyForm
materialises one set of children per row of submission data. Instance children
share their template's names across rows, so they are addressable by path
(`education[0].year`) and never by name.
"""

import unittest

from surveyjs import SurveyCreator, SurveyForm
from surveyjs.elements.paneldynamic import PanelInstance
from tests.utils import load_creator, load_form, readjson

NESTED_PANEL_SCHEMA = {
    'elements': [
        {'type': 'paneldynamic', 'name': 'pd', 'templateElements': [
            {'type': 'panel', 'name': 'grp', 'elements': [
                {'type': 'text', 'name': 'x'},
                {'type': 'text', 'name': 'y'},
            ]},
        ]},
    ],
}

NESTED_PANEL_DATA = {'pd': [{'x': 'x0', 'y': 'y0'}, {'x': 'x1', 'y': 'y1'}]}

COLLIDING_SCHEMA = {
    'elements': [
        {'type': 'paneldynamic', 'name': 'jobs',
         'templateElements': [{'type': 'text', 'name': 'year'}]},
        {'type': 'paneldynamic', 'name': 'school',
         'templateElements': [{'type': 'text', 'name': 'year'}]},
    ],
}


class TestCreatorHoldsTemplate(unittest.TestCase):
    """A Creator has no submission data, so it materialises no rows."""

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['education']

    def test_no_panels(self):
        self.assertEqual(self.q.panels, [])

    def test_template_children_keyed_by_name(self):
        self.assertEqual(list(self.q.elements), ['institution', 'degree', 'year'])

    def test_template_children_are_not_repeating(self):
        for child in self.q.elements.values():
            self.assertFalse(child.in_repeating_context)
            self.assertIsNone(child.panel_index)

    def test_template_child_path_has_no_index(self):
        year = self.survey.get_element_by_path('education.year')
        self.assertEqual(year.input_path, ['education', 'year'])


class TestFormMaterialisesPanels(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.all_elements['education']
        self.data = readjson('test_survey_form.json')

    def test_one_panel_per_row(self):
        self.assertEqual(len(self.q.panels), len(self.data['education']))
        for panel in self.q.panels:
            self.assertIsInstance(panel, PanelInstance)

    def test_panel_indices(self):
        self.assertEqual([p.index for p in self.q.panels], [0, 1])

    def test_panel_name(self):
        self.assertEqual(self.q.panels[0].name, 'education[0]')
        self.assertEqual(repr(self.q.panels[1]), '<PanelInstance name=education[1]>')

    def test_panel_children_carry_their_row_values(self):
        for panel, row in zip(self.q.panels, self.data['education']):
            for key, expected in row.items():
                self.assertEqual(panel.elements[key].value, expected)

    def test_rows_hold_distinct_values(self):
        self.assertEqual(self.q.panels[0]['institution'].value, 'MIT')
        self.assertEqual(self.q.panels[1]['institution'].value, 'Stanford')

    def test_panel_index_on_children(self):
        for panel in self.q.panels:
            for child in panel.elements.values():
                self.assertEqual(child.panel_index, panel.index)
                self.assertTrue(child.in_repeating_context)

    def test_children_parent_is_the_paneldynamic(self):
        for child in self.q.panels[0].elements.values():
            self.assertIs(child.parent, self.q)

    def test_children_inherit_page(self):
        for child in self.q.panels[0].elements.values():
            self.assertEqual(child.page.name, 'page_layout')

    def test_get_panel(self):
        self.assertIs(self.q.get_panel(1), self.q.panels[1])

    def test_get_panel_out_of_range(self):
        self.assertIsNone(self.q.get_panel(9))
        self.assertIsNone(self.q.get_panel(-1))

    def test_panel_data(self):
        self.assertEqual(self.q.panels[0].data, self.data['education'][0])

    def test_panel_dunders(self):
        panel = self.q.panels[0]
        self.assertEqual(len(panel), 3)
        self.assertEqual([e.name for e in panel], ['institution', 'degree', 'year'])
        self.assertEqual(panel.get('year').value, 2015)
        self.assertIsNone(panel.get('nope'))

    def test_panel_to_dict(self):
        data = self.q.panels[0].to_dict()
        self.assertEqual(data['name'], 'education[0]')
        self.assertEqual(data['index'], 0)
        self.assertEqual(len(data['elements']), 3)

    def test_paneldynamic_value_unchanged(self):
        """Materialising rows must not disturb the panel's own list value."""
        self.assertEqual(self.q.value, self.data['education'])


class TestInstanceChildrenAreNotNameAddressable(unittest.TestCase):
    """The whole reason instances are path-keyed: names repeat across rows."""

    def setUp(self):
        self.form = load_form()

    def test_absent_from_questions(self):
        for name in ('institution', 'degree', 'year'):
            self.assertNotIn(name, self.form.questions)

    def test_absent_from_all_elements(self):
        for name in ('institution', 'degree', 'year'):
            self.assertNotIn(name, self.form.all_elements)

    def test_paneldynamic_itself_is_still_name_addressable(self):
        self.assertIn('education', self.form.questions)
        self.assertIn('education', self.form.all_elements)

    def test_paneldynamic_elements_map_stays_empty_on_a_form(self):
        """Rows live in `panels`; `elements` would collide across them."""
        self.assertEqual(len(self.form.all_elements['education'].elements), 0)


class TestInstancePaths(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.data = readjson('test_survey_form.json')

    def test_indexed_paths_registered(self):
        keys = [k for k in self.form.all_element_paths if k.startswith('education')]
        self.assertEqual(keys, [
            'education',
            'education[0].institution', 'education[0].degree', 'education[0].year',
            'education[1].institution', 'education[1].degree', 'education[1].year',
        ])

    def test_get_element_by_indexed_path(self):
        element = self.form.get_element_by_path('education[1].institution')
        self.assertEqual(element.value, 'Stanford')

    def test_input_path_carries_int_index(self):
        year = self.form.get_element_by_path('education[0].year')
        self.assertEqual(year.input_path, ['education', 0, 'year'])
        self.assertEqual(year.input_path_str, 'education[0].year')

    def test_input_path_indexes_the_raw_data(self):
        """input_path must be directly usable against the submission dict."""
        for panel in self.form.all_elements['education'].panels:
            for child in panel.elements.values():
                container, index, key = child.input_path
                self.assertEqual(self.data[container][index][key], child.value)

    def test_get_value_from_round_trips(self):
        for panel in self.form.all_elements['education'].panels:
            for child in panel.elements.values():
                self.assertEqual(child.get_value_from(self.data), child.value)

    def test_get_value_from_missing_data(self):
        year = self.form.get_element_by_path('education[0].year')
        self.assertIsNone(year.get_value_from({}))
        self.assertIsNone(year.get_value_from({'education': []}))
        self.assertIsNone(year.get_value_from(None))


class TestNestedPanelInsidePaneldynamic(unittest.TestCase):
    """A panel repeats with its row but adds no data nesting level."""

    def setUp(self):
        self.creator = SurveyCreator(NESTED_PANEL_SCHEMA)
        self.form = SurveyForm(NESTED_PANEL_DATA, creator=self.creator)
        self.pd = self.form.all_elements['pd']

    def test_rows_materialised(self):
        self.assertEqual(len(self.pd.panels), 2)

    def test_inner_panel_repeats(self):
        grp = self.pd.panels[0]['grp']
        self.assertTrue(grp.in_repeating_context)
        self.assertEqual(grp.panel_index, 0)
        self.assertEqual(list(grp.elements), ['x', 'y'])

    def test_structural_path_includes_the_panel(self):
        child = self.form.get_element_by_path('pd[1].grp.y')
        self.assertEqual(child.path, ['pd[1]', 'grp', 'y'])

    def test_input_path_drops_the_panel_keeps_the_index(self):
        child = self.form.get_element_by_path('pd[1].grp.y')
        self.assertEqual(child.input_path, ['pd', 1, 'y'])
        self.assertEqual(child.get_value_from(NESTED_PANEL_DATA), 'y1')

    def test_values(self):
        self.assertEqual(self.form.get_element_by_path('pd[0].grp.x').value, 'x0')
        self.assertEqual(self.form.get_element_by_path('pd[1].grp.x').value, 'x1')

    def test_deep_children_not_name_addressable(self):
        for name in ('x', 'y', 'grp'):
            self.assertNotIn(name, self.form.questions)
            self.assertNotIn(name, self.form.all_elements)

    def test_creator_keeps_unindexed_template_paths(self):
        self.assertEqual(list(self.creator.all_element_paths), ['pd', 'pd.grp', 'pd.grp.x', 'pd.grp.y'])


class TestCollidingTemplateNames(unittest.TestCase):

    def setUp(self):
        self.form = SurveyForm(
            {'jobs': [{'year': '1999'}], 'school': [{'year': '2001'}, {'year': '2003'}]},
            creator=SurveyCreator(COLLIDING_SCHEMA),
        )

    def test_all_rows_addressable(self):
        self.assertEqual(
            list(self.form.all_element_paths),
            ['jobs', 'jobs[0].year', 'school', 'school[0].year', 'school[1].year'],
        )

    def test_values_do_not_shadow_each_other(self):
        self.assertEqual(self.form.get_element_by_path('jobs[0].year').value, '1999')
        self.assertEqual(self.form.get_element_by_path('school[1].year').value, '2003')


DEFAULTS_SCHEMA = {
    'elements': [
        {'type': 'paneldynamic', 'name': 'pd', 'templateElements': [
            {'type': 'text', 'name': 'nickname', 'defaultValue': 'anon'},
            {'type': 'dropdown', 'name': 'color', 'choices': [
                {'value': 'r', 'text': 'Red'}, {'value': 'b', 'text': 'Blue'}]},
        ]},
    ],
}


class TestGetPanelValue(unittest.TestCase):
    """`get_panel_value` reads through the element, like SurveyForm.get_value."""

    def setUp(self):
        self.creator = SurveyCreator(DEFAULTS_SCHEMA)
        # row 0 omits 'nickname'; row 1 supplies it
        self.form = SurveyForm(
            {'pd': [{'color': 'r'}, {'nickname': 'bob', 'color': 'b'}]},
            creator=self.creator,
        )
        self.q = self.form.questions['pd']

    def test_reads_supplied_value(self):
        self.assertEqual(self.q.get_panel_value(1, 'nickname'), 'bob')

    def test_honors_default_value_for_omitted_field(self):
        """The raw-dict lookup this replaced returned None here."""
        self.assertEqual(self.q.get_panel_value(0, 'nickname'), 'anon')

    def test_agrees_with_the_element(self):
        for index, panel in enumerate(self.q.panels):
            for name, element in panel.elements.items():
                self.assertEqual(self.q.get_panel_value(index, name), element.value)

    def test_out_of_range_index(self):
        self.assertIsNone(self.q.get_panel_value(99, 'nickname'))

    def test_negative_index_does_not_wrap(self):
        """-1 used to index the last row through Python's negative indexing."""
        self.assertIsNone(self.q.get_panel_value(-1, 'nickname'))

    def test_nonexistent_field(self):
        self.assertIsNone(self.q.get_panel_value(0, 'nonexistent'))

    def test_returns_none_on_a_creator(self):
        """A Creator holds the template, not rows."""
        self.assertIsNone(self.creator.questions['pd'].get_panel_value(0, 'nickname'))

    def test_derived_accessors_need_the_element_not_the_shortcut(self):
        """get_panel_value gives the value; the element gives the display text."""
        self.assertEqual(self.q.get_panel_value(0, 'color'), 'r')
        self.assertEqual(self.q.get_panel(0)['color'].value_text, 'Red')


class TestEmptyAndMissingRows(unittest.TestCase):

    def setUp(self):
        self.creator = SurveyCreator(NESTED_PANEL_SCHEMA)

    def test_missing_key_yields_no_panels(self):
        form = SurveyForm({}, creator=self.creator)
        self.assertEqual(form.all_elements['pd'].panels, [])
        self.assertIsNone(form.all_elements['pd'].get_panel(0))

    def test_empty_list_yields_no_panels(self):
        form = SurveyForm({'pd': []}, creator=self.creator)
        self.assertEqual(form.all_elements['pd'].panels, [])

    def test_non_dict_row_is_tolerated(self):
        form = SurveyForm({'pd': [None]}, creator=self.creator)
        self.assertEqual(len(form.all_elements['pd'].panels), 1)
        self.assertIsNone(form.get_element_by_path('pd[0].grp.x').value)


if __name__ == '__main__':
    unittest.main()
