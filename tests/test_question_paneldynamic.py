# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the paneldynamic question type."""

import unittest
from datetime import date

from surveyjs import SurveyCreator, SurveyForm
from surveyjs.elements.paneldynamic import QuestionPaneldynamic
from tests.utils import load_creator, load_form


class TestQuestionPaneldynamic(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['education']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionPaneldynamic)

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
        self.q = self.form.questions['education']

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



TYPED_SCHEMA = {'elements': [
    {'type': 'paneldynamic', 'name': 'jobs', 'templateElements': [
        {'type': 'text', 'name': 'start', 'inputType': 'date'},
        {'type': 'boolean', 'name': 'current', 'valueTrue': 'yes', 'valueFalse': 'no'},
        {'type': 'panel', 'name': 'details', 'elements': [
            {'type': 'text', 'name': 'hours', 'inputType': 'number'},
        ]},
        {'type': 'matrixdynamic', 'name': 'tasks', 'columns': [
            {'name': 'due', 'cellType': 'text', 'inputType': 'date'},
        ]},
    ]},
]}

TYPED_DATA = {'jobs': [
    {'start': '2024-03-15', 'current': 'yes', 'hours': '38',
     'tasks': [{'due': '2024-04-01'}], 'extra': 'kept'},
    {'start': 'bad-date', 'current': 'no'},
]}


class TestPanelDynamicValue(unittest.TestCase):
    """`value` is `raw_value` with every answer parsed by its own question."""

    def setUp(self):
        form = SurveyForm(TYPED_DATA, creator=SurveyCreator(TYPED_SCHEMA))
        self.q = form.questions['jobs']

    def test_value(self):
        self.assertEqual(self.q.value, [
            {'start': date(2024, 3, 15), 'current': True, 'hours': 38,
             'tasks': [{'due': date(2024, 4, 1)}], 'extra': 'kept'},
            {'start': None, 'current': False},
        ])

    def test_raw_value_untouched(self):
        self.assertEqual(self.q.raw_value, TYPED_DATA['jobs'])

    def test_panel_instance_value(self):
        self.assertEqual(self.q.get_panel(1).value, {'start': None, 'current': False})

    def test_creator_value_is_raw(self):
        """A Creator has no panel instances to parse with."""
        schema = {'elements': [dict(TYPED_SCHEMA['elements'][0],
                                    defaultValue=[{'start': '2024-03-15'}])]}
        q = SurveyCreator(schema).questions['jobs']
        self.assertEqual(q.value, [{'start': '2024-03-15'}])



NESTED_TEMPLATE_SCHEMA = {'elements': [
    {'type': 'paneldynamic', 'name': 'jobs', 'templateElements': [
        {'type': 'text', 'name': 'employer'},
        {'type': 'panel', 'name': 'details', 'elements': [
            {'type': 'text', 'name': 'start', 'inputType': 'date'},
            {'type': 'boolean', 'name': 'current'},
        ]},
        {'type': 'matrixdropdown', 'name': 'skills', 'rows': ['python', 'sql'],
         'columns': [{'name': 'level', 'cellType': 'rating'}]},
    ]},
]}

NESTED_TEMPLATE_DATA = {'jobs': [{'employer': 'Nova Code', 'start': '2020-01-06'}]}


class TestTemplatePanelNesting(unittest.TestCase):
    """`template_panel` is a blank row for rendering an empty form, so it must
    hold the whole template — including what nested containers build."""

    def assert_blank_row_complete(self, blank):
        details = blank['details']
        self.assertEqual(list(details.elements), ['start', 'current'])
        self.assertIsNone(details.elements['start'].value)
        self.assertEqual(details.elements['start'].path_str, 'jobs[0].details.start')
        self.assertEqual(list(blank['skills'].rows_cells), ['python', 'sql'])
        self.assertIsNone(blank['skills'].get_cell('python', 'level').value)

    def test_on_a_creator(self):
        creator = SurveyCreator(NESTED_TEMPLATE_SCHEMA)
        self.assert_blank_row_complete(creator.questions['jobs'].template_panel)

    def test_on_an_empty_form(self):
        form = SurveyForm({}, creator=SurveyCreator(NESTED_TEMPLATE_SCHEMA))
        self.assert_blank_row_complete(form.questions['jobs'].template_panel)

    def test_on_a_form_with_rows(self):
        form = SurveyForm(NESTED_TEMPLATE_DATA, creator=SurveyCreator(NESTED_TEMPLATE_SCHEMA))
        self.assert_blank_row_complete(form.questions['jobs'].template_panel)

    def test_nested_children_not_registered_by_name(self):
        """Building the blank row must not file its children on the owner."""
        creator = SurveyCreator(NESTED_TEMPLATE_SCHEMA)
        template_start = creator.questions['start']
        blank = creator.questions['jobs'].template_panel
        self.assertIs(creator.questions['start'], template_start)
        self.assertIsNot(blank['details'].elements['start'], template_start)


class TestTemplatePanelData(unittest.TestCase):
    """The blank row stands for no row: it never reads a submitted one."""

    def test_empty_form(self):
        form = SurveyForm({}, creator=SurveyCreator(NESTED_TEMPLATE_SCHEMA))
        blank = form.questions['jobs'].template_panel
        self.assertEqual(blank.data, {})
        self.assertEqual(blank.value, {})

    def test_form_with_rows(self):
        """Index 0, yet not row 0's data."""
        form = SurveyForm(NESTED_TEMPLATE_DATA, creator=SurveyCreator(NESTED_TEMPLATE_SCHEMA))
        jobs = form.questions['jobs']
        self.assertEqual(jobs.template_panel.data, {})
        self.assertIsNone(jobs.template_panel['employer'].value)
        self.assertEqual(jobs.get_panel(0).data, NESTED_TEMPLATE_DATA['jobs'][0])

    def test_non_dict_row_kept_as_submitted(self):
        form = SurveyForm({'jobs': ['junk']}, creator=SurveyCreator(NESTED_TEMPLATE_SCHEMA))
        jobs = form.questions['jobs']
        self.assertEqual(jobs.get_panel(0).data, 'junk')
        self.assertEqual(jobs.value, ['junk'])


if __name__ == '__main__':
    unittest.main()
