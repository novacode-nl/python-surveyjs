# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for value specs: `value_spec()`, `check_value()` and `check_values()`."""

import json
import unittest
from datetime import date

from surveyjs import SurveyCreator, SurveyForm
from tests.utils import load_creator

SCHEMA = {
    'pages': [{
        'name': 'p1',
        'elements': [
            {'type': 'text', 'name': 'name'},
            {'type': 'text', 'name': 'birth', 'inputType': 'date'},
            {'type': 'text', 'name': 'meeting', 'inputType': 'datetime-local'},
            {'type': 'text', 'name': 'age', 'inputType': 'number', 'min': 0, 'max': 120},
            {'type': 'boolean', 'name': 'subscribed'},
            {'type': 'boolean', 'name': 'consent', 'valueTrue': 'agreed', 'valueFalse': 'declined'},
            {'type': 'dropdown', 'name': 'level', 'choices': [1, 2, 3]},
            {'type': 'dropdown', 'name': 'partner',
             'choicesByUrl': {'url': '/formio/data/res.partner', 'valueName': 'id'}},
            {'type': 'checkbox', 'name': 'colors', 'choices': ['red', 'blue'],
             'showOtherItem': True, 'maxSelectedChoices': 2},
            {'type': 'expression', 'name': 'total', 'expression': '{age} * 2'},
            {'type': 'html', 'name': 'intro', 'html': '<p>Hi</p>'},
            {'type': 'panel', 'name': 'contact', 'elements': [
                {'type': 'text', 'name': 'phone'},
            ]},
            {'type': 'multipletext', 'name': 'address', 'items': [
                {'name': 'street'},
                {'name': 'since', 'inputType': 'month'},
            ]},
            {'type': 'matrixdynamic', 'name': 'lines', 'columns': [
                {'name': 'product', 'cellType': 'text'},
                {'name': 'qty', 'cellType': 'text', 'inputType': 'number'},
                {'name': 'subtotal', 'cellType': 'expression', 'expression': '{row.qty}'},
            ]},
            {'type': 'paneldynamic', 'name': 'jobs', 'templateElements': [
                {'type': 'text', 'name': 'employer'},
                {'type': 'text', 'name': 'year', 'inputType': 'number'},
            ]},
        ],
    }],
}


class TestValueSpec(unittest.TestCase):

    def setUp(self):
        self.creator = SurveyCreator(SCHEMA)
        self.q = self.creator.all_element_paths

    def test_text_input_types(self):
        self.assertEqual(self.q['name'].value_spec(), {'type': 'string'})
        self.assertEqual(self.q['birth'].value_spec(),
                         {'type': 'string', 'format': 'date', 'examples': ['2024-03-15']})
        self.assertEqual(self.q['age'].value_spec(),
                         {'type': 'number', 'minimum': 0, 'maximum': 120})

    def test_string_bounds_are_left_out(self):
        creator = SurveyCreator({'elements': [
            {'type': 'text', 'name': 'qty', 'inputType': 'number', 'min': '0'}]})
        self.assertEqual(creator.questions['qty'].value_spec(), {'type': 'number'})
        self.assertEqual(creator.questions['qty'].check_value(5), [])

    def test_boolean(self):
        self.assertEqual(self.q['subscribed'].value_spec(), {'type': 'boolean'})
        self.assertEqual(self.q['consent'].value_spec(), {'enum': ['agreed', 'declined']})

    def test_choices(self):
        self.assertEqual(self.q['level'].value_spec(), {'enum': [1, 2, 3]})
        self.assertEqual(self.q['colors'].value_spec(), {
            'type': 'array', 'items': {'enum': ['red', 'blue', 'other']}, 'maxItems': 2})

    def test_choices_by_url(self):
        self.assertEqual(self.q['partner'].value_spec(), {
            'x-choicesByUrl': {'url': '/formio/data/res.partner', 'valueName': 'id'}})

    def test_no_value(self):
        self.assertIsNone(self.q['total'].value_spec())
        self.assertIsNone(self.q['intro'].value_spec())
        self.assertIsNone(self.q['contact'].value_spec())

    def test_matrixdynamic_leaves_out_computed_column(self):
        row = self.q['lines'].value_spec()['items']
        self.assertEqual(list(row['properties']), ['product', 'qty'])
        self.assertEqual(row['properties']['qty'], {'type': 'number'})

    def test_paneldynamic(self):
        self.assertEqual(self.q['jobs'].value_spec(), {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {'employer': {'type': 'string'}, 'year': {'type': 'number'}},
                'additionalProperties': False,
            },
        })

    def test_creator_spec_top_level(self):
        spec = self.creator.value_spec()
        self.assertFalse(spec['additionalProperties'])
        # A plain panel's question is at the top level; layout and computed
        # elements, and a dynamic panel's questions, are not.
        self.assertIn('phone', spec['properties'])
        for name in ('contact', 'intro', 'total', 'employer'):
            self.assertNotIn(name, spec['properties'])

    def test_spec_is_json(self):
        # The full test schema covers every supported question type.
        json.dumps(load_creator().value_spec())

    def test_form_elements_have_specs(self):
        form = SurveyForm({'name': 'Bob'}, creator=self.creator)
        self.assertEqual(form.questions['birth'].value_spec()['format'], 'date')


class TestCheckValue(unittest.TestCase):

    def setUp(self):
        self.creator = SurveyCreator(SCHEMA)
        self.q = self.creator.all_element_paths

    def test_fits(self):
        self.assertEqual(self.q['birth'].check_value('2024-03-15'), [])
        self.assertEqual(self.q['meeting'].check_value('2024-03-15T13:45'), [])
        self.assertEqual(self.q['consent'].check_value('agreed'), [])
        self.assertEqual(self.q['partner'].check_value(42), [])

    def test_none_always_fits(self):
        for path in ('name', 'birth', 'colors', 'jobs'):
            self.assertEqual(self.q[path].check_value(None), [])

    def test_date_object(self):
        self.assertEqual(self.q['birth'].check_value(date(2024, 3, 15)), [
            "birth: expected a string in the format YYYY-MM-DD (e.g. '2024-03-15'), got date"])

    def test_date_wrong_format(self):
        problems = self.q['birth'].check_value('15-03-2024')
        self.assertEqual(len(problems), 1)
        self.assertIn('does not fit', problems[0])

    def test_number(self):
        self.assertEqual(self.q['age'].check_value('42'), ['age: expected a number, got str'])
        self.assertEqual(self.q['age'].check_value(True), ['age: expected a number, got bool'])
        self.assertEqual(self.q['age'].check_value(130), ['age: expected a number of at most 120'])

    def test_enum_is_strict(self):
        # True == 1 in Python, but not in the form's data.
        self.assertEqual(len(self.q['level'].check_value(True)), 1)
        self.assertEqual(len(self.q['level'].check_value('1')), 1)
        self.assertEqual(self.q['level'].check_value(1), [])

    def test_checkbox(self):
        self.assertEqual(self.q['colors'].check_value('red'),
                         ['colors: expected a list, got str'])
        self.assertEqual(len(self.q['colors'].check_value(['red', 'blue', 'other'])), 1)
        self.assertIn('colors[1]:', self.q['colors'].check_value(['red', 'pink'])[0])

    def test_nested_paths(self):
        problems = self.q['jobs'].check_value([
            {'employer': 'Acme', 'year': 2020},
            {'employer': 'Initech', 'year': '2021', 'boss': 'Bill'},
        ])
        self.assertEqual(problems, [
            'jobs[1].year: expected a number, got str',
            "jobs[1].boss: unknown key; expected one of ['employer', 'year']",
        ])

    def test_multipletext(self):
        self.assertEqual(self.q['address'].check_value({'since': '2024-03-01'}), [
            "address.since: expected a string in the format YYYY-MM (e.g. '2024-03'), "
            "got a str that does not fit"])

    def test_no_value(self):
        self.assertEqual(self.q['total'].check_value(5),
                         ['total: holds no value (type expression)'])


class TestCheckValues(unittest.TestCase):

    def setUp(self):
        self.creator = SurveyCreator(SCHEMA)

    def test_fits(self):
        self.assertEqual(self.creator.check_values({
            'name': 'Bob', 'phone': '+31 6', 'colors': ['red'],
            'lines': [{'product': 'Pen', 'qty': 2}],
        }), [])

    def test_not_a_dict(self):
        self.assertEqual(self.creator.check_values([]), [
            'expected an object (dict) keyed by question name, got list'])

    def test_unknown_name(self):
        self.assertEqual(self.creator.check_values({'nmae': 'Bob'}),
                         ['nmae: no question has this name'])

    def test_nested_name(self):
        problems = self.creator.check_values({'employer': 'Acme'})
        self.assertEqual(len(problems), 1)
        self.assertIn("part of 'jobs'", problems[0])

    def test_layout_and_computed(self):
        problems = self.creator.check_values({'contact': 'x', 'total': 1})
        self.assertEqual(problems, [
            'contact: holds no value (type panel)',
            'total: holds no value (type expression)',
        ])

    def test_messages_never_contain_values(self):
        secret = 'S3CRET-VALUE'
        problems = self.creator.check_values({
            'birth': secret, 'age': secret, 'level': secret, 'colors': [secret],
            'jobs': [{'year': secret}], 'address': {'since': secret},
        })
        self.assertEqual(len(problems), 6)
        for problem in problems:
            self.assertNotIn(secret, problem)


if __name__ == '__main__':
    unittest.main()
