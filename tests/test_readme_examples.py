# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Executes the README's Usage Examples, so documentation cannot rot silently.

Each test mirrors one snippet in README.md. If a snippet's output changes, the
matching test fails and the README must be updated with it.
"""

import unittest
from datetime import date, datetime, timedelta

from surveyjs import SurveyCreator, SurveyForm, register_input_type
from surveyjs.elements.inputtype import INPUT_TYPE_PARSERS
from surveyjs.elements.text import QuestionText
from surveyjs.elements.validators import VALIDATORS, register_validator

CREATOR_JSON = {
    'title': 'Demo',
    'pages': [
        {'name': 'personal', 'title': 'Personal', 'elements': [
            {'type': 'text', 'name': 'firstName', 'title': 'First Name'},
            {'type': 'text', 'name': 'birthDate', 'title': 'Birth Date', 'inputType': 'date'},
            {'type': 'text', 'name': 'appointment', 'title': 'Appointment',
             'inputType': 'datetime-local'},
            {'type': 'panel', 'name': 'contact', 'elements': [
                {'type': 'text', 'name': 'phone', 'title': 'Phone'},
                {'type': 'panel', 'name': 'address', 'elements': [
                    {'type': 'text', 'name': 'city', 'title': 'City'}]}]},
        ]},
        {'name': 'history', 'title': 'History', 'elements': [
            {'type': 'paneldynamic', 'name': 'education', 'templateElements': [
                {'type': 'text', 'name': 'school'},
                {'type': 'text', 'name': 'graduated', 'inputType': 'date'},
                {'type': 'panel', 'name': 'details', 'elements': [
                    {'type': 'text', 'name': 'degree'}]}]},
            {'type': 'matrixdynamic', 'name': 'jobs', 'cellType': 'text', 'columns': [
                {'name': 'employer'},
                {'name': 'started', 'cellType': 'text', 'inputType': 'date'},
                {'name': 'role', 'cellType': 'dropdown', 'choices': [
                    {'value': 'dev', 'text': 'Developer'},
                    {'value': 'design', 'text': 'Designer'}]}]},
            {'type': 'matrixdropdown', 'name': 'budget',
             'columns': [{'name': 'status', 'cellType': 'dropdown', 'choices': [
                 {'value': 'open', 'text': 'Open'},
                 {'value': 'done', 'text': 'Done'}]}],
             'rows': [{'value': 'marketing', 'text': 'Marketing'}]},
            {'type': 'multipletext', 'name': 'dates', 'items': [
                {'name': 'from', 'inputType': 'date'}]},
            {'type': 'boolean', 'name': 'consent',
             'valueTrue': 'agreed', 'valueFalse': 'declined'},
        ]},
    ],
}

#: The README's Validation section: a schema of its own, since the demo
#: submission above is valid and an error needs a rule to break.
VALIDATION_JSON = {
    'elements': [
        {'type': 'text', 'name': 'email', 'title': 'Email', 'isRequired': True,
         'validators': [{'type': 'email'}]},
        {'type': 'text', 'name': 'age', 'title': 'Age', 'inputType': 'number',
         'validators': [{'type': 'numeric', 'minValue': 18}]},
    ],
}

FORM_JSON = {
    'firstName': 'Bob',
    'birthDate': '1985-06-14',
    'appointment': '2024-03-15T13:45',
    'phone': '+31 6 1234 5678',
    'city': 'Amsterdam',
    'education': [{'school': 'MIT', 'graduated': '2015-05-30', 'degree': 'MSc'}],
    'jobs': [{'employer': 'Nova Code', 'started': '2020-01-06', 'role': 'dev'}],
    'budget': {'marketing': {'status': 'done'}},
    'dates': {'from': '2024-07-08'},
    'consent': 'agreed',
}

#: The README's Translations section.
TRANSLATION_JSON = {
    'elements': [
        {'type': 'boolean', 'name': 'agree',
         'title': {'default': 'I agree', 'fr': "J'accepte"}},
        {'type': 'dropdown', 'name': 'color', 'choices': ['Red', 'Blue']},
    ],
}

TRANSLATION_I18N = {'fr': {'Yes': 'Oui', 'No': 'Non', 'Red': 'Rouge', 'Blue': 'Bleu'}}

TRANSLATION_FORM_JSON = {'agree': True, 'color': 'Red'}


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

    def test_date_question_yields_a_date_not_a_datetime(self):
        """datetime subclasses date, so assertEqual alone would not catch it."""
        self.assertNotIsInstance(self.form.questions['birthDate'].value, datetime)

    def test_datetime_question_yields_a_datetime(self):
        q = self.form.questions['appointment']
        self.assertEqual(q.value, datetime(2024, 3, 15, 13, 45))
        self.assertIsInstance(q.value, datetime)
        self.assertEqual(q.raw_value, '2024-03-15T13:45')

    def test_boolean_value_and_value_text(self):
        q = self.form.questions['consent']
        self.assertEqual(q.raw_value, 'agreed')
        self.assertIs(q.value, True)
        self.assertEqual(q.value_text, 'Yes')

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

    def test_both_classes_have_pages(self):
        self.assertEqual([page.name for page in self.creator.pages], ['personal', 'history'])
        self.assertEqual([page.name for page in self.form.pages], ['personal', 'history'])

    def test_page_title(self):
        self.assertEqual(self.form.pages[0].title, 'Personal')

    def test_get_page_by_name_on_either_class(self):
        self.assertEqual(repr(self.form.get_page_by_name('history')), '<Page name=history>')
        self.assertEqual(repr(self.creator.get_page_by_name('history')), '<Page name=history>')

    def test_page_elements_are_objects_keyed_by_name(self):
        """`elements` is an OrderedDict of Element objects; list() gives keys."""
        elements = self.form.pages[0].elements
        self.assertEqual(list(elements),
                         ['firstName', 'birthDate', 'appointment', 'contact'])
        self.assertEqual(repr(elements['firstName']),
                         '<QuestionText name=firstName input_type=text>')
        self.assertEqual(
            [repr(e) for e in elements.values()],
            ['<QuestionText name=firstName input_type=text>',
             '<QuestionText name=birthDate input_type=date>',
             '<QuestionText name=appointment input_type=datetime-local>',
             '<QuestionPanel name=contact>'],
        )

    def test_page_questions_excludes_layout(self):
        self.assertEqual(list(self.form.pages[0].questions),
                         ['firstName', 'birthDate', 'appointment'])

    def test_values_come_from_a_form_page(self):
        self.assertEqual(self.form.pages[0].elements['firstName'].value, 'Bob')
        self.assertEqual(self.form.pages[0].elements['birthDate'].value, date(1985, 6, 14))

    def test_a_creator_page_element_has_no_submitted_value(self):
        """A creator describes the schema; only a form carries submission data."""
        self.assertIsNone(self.creator.pages[0].elements['birthDate'].value)

    def test_creator_and_form_pages_hold_distinct_elements(self):
        self.assertIsNot(self.form.pages[0].elements['firstName'],
                         self.creator.pages[0].elements['firstName'])

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

    def test_nested_panels_path(self):
        city = self.form.all_elements['city']
        self.assertEqual(city.path, ['contact', 'address', 'city'])
        self.assertEqual(city.path_str, 'contact.address.city')
        self.assertEqual(city.input_path, ['city'])
        self.assertEqual(self.form.get_element_by_path('contact.address.city').value,
                         'Amsterdam')

    def test_panel_in_dynamic_panel_row_path(self):
        degree = self.form.get_element_by_path('education[0].details.degree')
        self.assertEqual(degree.path, ['education[0]', 'details', 'degree'])
        self.assertEqual(degree.input_path, ['education', 0, 'degree'])
        self.assertEqual(degree.input_path_str, 'education[0].degree')
        self.assertEqual(degree.value, 'MSc')

    # --- Dynamic panels ---

    def test_panels_repr(self):
        self.assertEqual(repr(self.form.questions['education'].panels),
                         '[<PanelInstance name=education[0]>]')

    def test_panel_child_value_is_parsed(self):
        self.assertEqual(self.form.questions['education'].panels[0]['graduated'].value,
                         date(2015, 5, 30))

    def test_panel_value_is_a_parsed_copy(self):
        education = self.form.questions['education']
        self.assertEqual(education.value,
                         [{'school': 'MIT', 'graduated': date(2015, 5, 30), 'degree': 'MSc'}])
        self.assertEqual(education.raw_value,
                         [{'school': 'MIT', 'graduated': '2015-05-30', 'degree': 'MSc'}])

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
        self.assertEqual(
            self.form.questions['jobs'].get_row_value(0),
            {'employer': 'Nova Code', 'started': date(2020, 1, 6), 'role': 'dev'})

    def test_matrix_value_is_a_parsed_copy(self):
        jobs = self.form.questions['jobs']
        self.assertEqual(jobs.value, [
            {'employer': 'Nova Code', 'started': date(2020, 1, 6), 'role': 'dev'}])
        self.assertEqual(jobs.raw_value, [
            {'employer': 'Nova Code', 'started': '2020-01-06', 'role': 'dev'}])

    def test_multipletext_item_values(self):
        self.assertEqual(self.form.questions['dates'].item_values,
                         {'from': date(2024, 7, 8)})

    def test_multipletext_value_is_a_parsed_copy(self):
        dates = self.form.questions['dates']
        self.assertEqual(dates.value, {'from': date(2024, 7, 8)})
        self.assertEqual(dates.raw_value, {'from': '2024-07-08'})

    # --- Matrix cells as questions ---

    def test_cell_is_a_question_of_its_column_cell_type(self):
        cell = self.form.questions['jobs'].get_cell(0, 'role')
        self.assertEqual(repr(cell), '<QuestionDropdown name=role>')
        self.assertEqual(cell.value, 'dev')

    def test_cell_behaves_like_its_type(self):
        """The point of the exercise: a dropdown cell resolves its choices."""
        self.assertEqual(self.form.questions['jobs'].get_cell(0, 'role').value_text,
                         'Developer')

    def test_cells_of_one_row_and_every_row(self):
        jobs = self.form.questions['jobs']
        self.assertEqual(list(jobs.cells(0)), ['employer', 'started', 'role'])
        self.assertEqual(
            [repr(cell) for cell in jobs.cells(0).values()],
            ['<QuestionText name=employer input_type=text>',
             '<QuestionText name=started input_type=date>',
             '<QuestionDropdown name=role>'],
        )
        self.assertEqual(list(jobs.rows_cells), [0])

    def test_column_cell_raw(self):
        self.assertEqual(
            self.form.questions['jobs'].get_column('started').cell_raw,
            {'name': 'started', 'cellType': 'text', 'inputType': 'date', 'type': 'text'})

    def test_a_creator_materialises_no_cells(self):
        """A schema has no submission, so it has no rows."""
        self.assertEqual(self.creator.questions['jobs'].rows_cells, {})

    def test_cells_are_addressed_by_path_never_by_name(self):
        self.assertEqual(self.form.get_element_by_path('jobs[0].role').value_text,
                         'Developer')
        self.assertEqual(self.form.questions['jobs'].get_cell(0, 'started').input_path,
                         ['jobs', 0, 'started'])
        self.assertNotIn('role', self.form.questions)

    def test_matrixdropdown_rows_are_keyed_by_name(self):
        self.assertEqual(self.form.questions['budget'].row_names, ['marketing'])
        cell = self.form.get_element_by_path('budget[marketing].status')
        self.assertEqual(cell.value_text, 'Done')
        self.assertEqual(cell.input_path, ['budget', 'marketing', 'status'])

    # --- Translations ---

    def test_translations(self):
        creator = SurveyCreator(TRANSLATION_JSON, language='fr', i18n=TRANSLATION_I18N)
        form = SurveyForm(TRANSLATION_FORM_JSON, creator)
        self.assertEqual(form.questions['agree'].title, "J'accepte")
        self.assertEqual(form.questions['agree'].value_text, 'Oui')
        self.assertEqual(form.questions['color'].value_text, 'Rouge')

    def test_explicit_lang_on_a_shared_creator(self):
        creator = SurveyCreator(TRANSLATION_JSON, language='fr', i18n=TRANSLATION_I18N)
        form_en = SurveyForm(TRANSLATION_FORM_JSON, creator, lang='default')
        self.assertEqual(form_en.questions['agree'].title, 'I agree')
        self.assertEqual(form_en.questions['agree'].value_text, 'Yes')
        self.assertEqual(SurveyForm(TRANSLATION_FORM_JSON, creator)
                         .questions['agree'].value_text, 'Oui')

    # --- Validation ---

    def test_form_validation_errors_keyed_by_question_name(self):
        creator = SurveyCreator(VALIDATION_JSON)
        form = SurveyForm({'email': 'not-an-address', 'age': '16'}, creator)
        self.assertEqual(
            form.validation_errors(),
            {'email': {'email': 'Please enter a valid e-mail address.'},
             'age': {'numeric': "The 'Age' should be at least 18"}})

    def test_question_validation_errors_keyed_by_error_type(self):
        form = SurveyForm({'email': 'not-an-address', 'age': '16'},
                          SurveyCreator(VALIDATION_JSON))
        self.assertEqual(form.questions['age'].validation_errors(),
                         {'numeric': "The 'Age' should be at least 18"})
        self.assertFalse(form.questions['age'].is_empty())

    def test_required_fires_only_on_an_empty_answer(self):
        form = SurveyForm({'email': ''}, SurveyCreator(VALIDATION_JSON))
        self.assertEqual(form.validation_errors(),
                         {'email': {'required': 'Email is required'}})

    def test_a_valid_submission_yields_an_empty_dict(self):
        form = SurveyForm({'email': 'bob@novaforms.io', 'age': '42'},
                          SurveyCreator(VALIDATION_JSON))
        self.assertEqual(form.validation_errors(), {})

    # --- Extending ---

    def test_register_validator(self):
        snapshot = dict(VALIDATORS)
        self.addCleanup(lambda: (VALIDATORS.clear(), VALIDATORS.update(snapshot)))

        @register_validator('creditcard')
        def _creditcard(value, rule, element):
            return None if str(value).startswith('4') else 'Invalid card number.'

        creator = SurveyCreator({'elements': [
            {'type': 'text', 'name': 'card', 'title': 'Card',
             'validators': [{'type': 'creditcard'}]}]})
        self.assertEqual(SurveyForm({'card': '1234'}, creator).validation_errors(),
                         {'card': {'creditcard': 'Invalid card number.'}})
        self.assertEqual(SurveyForm({'card': '4111'}, creator).validation_errors(), {})

    def test_element_class_mapping_with_a_class(self):
        class MyText(QuestionText):
            @property
            def value(self):
                return (super().value or '').strip()

        creator = SurveyCreator({'elements': [{'type': 'text', 'name': 'a'}]},
                                element_class_mapping={'text': MyText})
        form = SurveyForm({'a': '  padded  '}, creator)
        self.assertIsInstance(form.questions['a'], MyText)
        self.assertEqual(form.questions['a'].value, 'padded')

    def test_unmapped_type_resolves_by_convention(self):
        creator = SurveyCreator({'elements': [{'type': 'text', 'name': 'a'}]})
        self.assertIsInstance(creator.questions['a'], QuestionText)


if __name__ == '__main__':
    unittest.main()
