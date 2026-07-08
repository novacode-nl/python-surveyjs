# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Executes the README's Usage Examples, so documentation cannot rot silently.

Each test mirrors one snippet in README.md. If a snippet's output changes, the
matching test fails and the README must be updated with it.
"""

import unittest
from datetime import date, timedelta

from surveyjs import SurveyCreator, SurveyForm, register_input_type
from surveyjs.elements.inputtype import INPUT_TYPE_PARSERS

CREATOR_JSON = {
    'title': 'Demo',
    'pages': [
        {'name': 'personal', 'title': 'Personal', 'elements': [
            {'type': 'text', 'name': 'firstName', 'title': 'First Name'},
            {'type': 'text', 'name': 'birthDate', 'title': 'Birth Date', 'inputType': 'date'},
            {'type': 'panel', 'name': 'contact', 'elements': [
                {'type': 'text', 'name': 'phone', 'title': 'Phone'}]},
        ]},
        {'name': 'history', 'title': 'History', 'elements': [
            {'type': 'paneldynamic', 'name': 'education', 'templateElements': [
                {'type': 'text', 'name': 'school'},
                {'type': 'text', 'name': 'graduated', 'inputType': 'date'}]},
            {'type': 'matrixdynamic', 'name': 'jobs', 'cellType': 'text', 'columns': [
                {'name': 'employer'},
                {'name': 'started', 'cellType': 'text', 'inputType': 'date'}]},
            {'type': 'multipletext', 'name': 'dates', 'items': [
                {'name': 'from', 'inputType': 'date'}]},
        ]},
    ],
}

FORM_JSON = {
    'firstName': 'Bob',
    'birthDate': '1985-06-14',
    'phone': '+31 6 1234 5678',
    'education': [{'school': 'MIT', 'graduated': '2015-05-30'}],
    'jobs': [{'employer': 'Nova Code', 'started': '2020-01-06'}],
    'dates': {'from': '2024-07-08'},
}


class TestReadmeExamples(unittest.TestCase):

    def setUp(self):
        self.creator = SurveyCreator(CREATOR_JSON)
        self.form = SurveyForm(FORM_JSON, self.creator)

    # --- Questions and values ---

    def test_label_and_value(self):
        self.assertEqual(self.form.questions['firstName'].label, 'First Name')
        self.assertEqual(self.form.questions['firstName'].value, 'Bob')

    def test_panel_repr(self):
        self.assertEqual(repr(self.form.elements['contact']), '<QuestionPanel name=contact>')

    # --- Input types: value vs raw_value ---

    def test_value_is_parsed_raw_value_is_not(self):
        q = self.form.questions['birthDate']
        self.assertEqual(q.value, date(1985, 6, 14))
        self.assertEqual(q.raw_value, '1985-06-14')

    def test_value_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.form.questions['birthDate'].value = '2000-01-01'

    def test_unparseable_value_is_none_but_raw_survives(self):
        form = SurveyForm({'birthDate': 'nonsense'}, self.creator)
        self.assertIsNone(form.questions['birthDate'].value)
        self.assertEqual(form.questions['birthDate'].raw_value, 'nonsense')

    def test_register_input_type(self):
        snapshot = dict(INPUT_TYPE_PARSERS)
        self.addCleanup(lambda: (INPUT_TYPE_PARSERS.clear(),
                                 INPUT_TYPE_PARSERS.update(snapshot)))
        register_input_type('duration', lambda v: timedelta(seconds=int(v)))
        form = SurveyForm({'elapsed': '90'}, creator=SurveyCreator(
            {'elements': [{'type': 'text', 'name': 'elapsed', 'inputType': 'duration'}]}))
        self.assertEqual(form.questions['elapsed'].value, timedelta(seconds=90))

    # --- Pages ---

    def test_page_names(self):
        self.assertEqual([page.name for page in self.creator.pages], ['personal', 'history'])

    def test_page_title(self):
        self.assertEqual(self.creator.pages[0].title, 'Personal')

    def test_page_elements_are_objects_keyed_by_name(self):
        """`elements` is an OrderedDict of Element objects; list() gives keys."""
        elements = self.creator.pages[0].elements
        self.assertEqual(list(elements), ['firstName', 'birthDate', 'contact'])
        self.assertEqual(repr(elements['firstName']), '<QuestionText name=firstName>')
        self.assertEqual(
            [repr(e) for e in elements.values()],
            ['<QuestionText name=firstName>',
             '<QuestionText name=birthDate>',
             '<QuestionPanel name=contact>'],
        )

    def test_page_questions_excludes_layout(self):
        self.assertEqual(list(self.creator.pages[0].questions), ['firstName', 'birthDate'])

    def test_element_knows_its_page(self):
        self.assertEqual(self.form.questions['birthDate'].page.name, 'personal')

    def test_implicit_page_for_pageless_schema(self):
        creator = SurveyCreator({'elements': [{'type': 'text', 'name': 'a'}]})
        self.assertEqual(len(creator.pages), 1)

    # --- Paths ---

    def test_path_str(self):
        self.assertEqual(self.form.all_elements['phone'].path_str, 'contact.phone')

    def test_panel_is_transparent_to_input_path(self):
        self.assertEqual(self.form.all_elements['phone'].input_path, ['phone'])

    def test_get_element_by_path(self):
        self.assertEqual(self.form.get_element_by_path('contact.phone').value,
                         '+31 6 1234 5678')

    # --- Dynamic panels ---

    def test_panels_repr(self):
        self.assertEqual(repr(self.form.questions['education'].panels),
                         '[<PanelInstance name=education[0]>]')

    def test_panel_child_value_is_parsed(self):
        self.assertEqual(self.form.questions['education'].panels[0]['graduated'].value,
                         date(2015, 5, 30))

    def test_get_panel_value(self):
        self.assertEqual(self.form.questions['education'].get_panel_value(0, 'school'), 'MIT')

    def test_panel_child_input_path_indexes_the_data(self):
        element = self.form.get_element_by_path('education[0].graduated')
        self.assertEqual(element.input_path, ['education', 0, 'graduated'])
        self.assertEqual(element.get_value_from(FORM_JSON), '2015-05-30')

    def test_instance_children_absent_from_name_maps(self):
        for name in ('school', 'graduated'):
            self.assertNotIn(name, self.form.questions)
            self.assertNotIn(name, self.form.all_elements)

    # --- Matrix columns and multipletext items ---

    def test_column_input_type(self):
        self.assertEqual(self.form.questions['jobs'].get_column('started').input_type, 'date')

    def test_cell_value_and_raw(self):
        jobs = self.form.questions['jobs']
        self.assertEqual(jobs.get_cell_value(0, 'started'), date(2020, 1, 6))
        self.assertEqual(jobs.get_cell_raw_value(0, 'started'), '2020-01-06')

    def test_row_value(self):
        self.assertEqual(self.form.questions['jobs'].get_row_value(0),
                         {'employer': 'Nova Code', 'started': date(2020, 1, 6)})

    def test_multipletext_item_values(self):
        self.assertEqual(self.form.questions['dates'].item_values,
                         {'from': date(2024, 7, 8)})


if __name__ == '__main__':
    unittest.main()
