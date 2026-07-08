# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for `inputType` parsing (dates, times, numbers) and its registry."""

import json
import unittest
from datetime import date, datetime, time, timedelta

from surveyjs import SurveyCreator, SurveyForm, parse_input_value, register_input_type
from surveyjs.elements.inputtype import (
    INPUT_TYPE_PARSERS,
    get_input_type_parser,
    parse_date,
    parse_datetime,
    parse_month,
    parse_number,
    parse_time,
    parse_week,
)
from surveyjs.elements.multipletext import MultipleTextItem
from tests.utils import load_form

TYPED_SCHEMA = {'elements': [
    {'type': 'text', 'name': 'd', 'inputType': 'date'},
    {'type': 'text', 'name': 'dt', 'inputType': 'datetime-local'},
    {'type': 'text', 'name': 't', 'inputType': 'time'},
    {'type': 'text', 'name': 'm', 'inputType': 'month'},
    {'type': 'text', 'name': 'w', 'inputType': 'week'},
    {'type': 'text', 'name': 'n', 'inputType': 'number'},
    {'type': 'text', 'name': 'r', 'inputType': 'range'},
    {'type': 'text', 'name': 'plain'},
    {'type': 'text', 'name': 'mail', 'inputType': 'email'},
]}

TYPED_DATA = {
    'd': '2024-03-15', 'dt': '2024-03-15T13:45', 't': '13:45',
    'm': '2024-03', 'w': '2024-W11', 'n': '42', 'r': '4.2',
    'plain': 'hi', 'mail': 'a@b.c',
}


def make_form(schema, data):
    return SurveyForm(data, creator=SurveyCreator(schema))


class TestParsers(unittest.TestCase):
    """The parsers, independent of any element."""

    def test_parse_date(self):
        self.assertEqual(parse_date('2024-03-15'), date(2024, 3, 15))

    def test_parse_date_narrows_a_datetime(self):
        """datetime subclasses date, so it must be narrowed, not passed through."""
        result = parse_date(datetime(2024, 3, 15, 13, 45))
        self.assertEqual(result, date(2024, 3, 15))
        self.assertNotIsInstance(result, datetime)

    def test_parse_date_passes_through_a_date(self):
        self.assertEqual(parse_date(date(2024, 3, 15)), date(2024, 3, 15))

    def test_parse_datetime_without_seconds(self):
        self.assertEqual(parse_datetime('2024-03-15T13:45'), datetime(2024, 3, 15, 13, 45))

    def test_parse_datetime_with_seconds(self):
        self.assertEqual(parse_datetime('2024-03-15T13:45:30'), datetime(2024, 3, 15, 13, 45, 30))

    def test_parse_datetime_space_separator(self):
        self.assertEqual(parse_datetime('2024-03-15 13:45:30'), datetime(2024, 3, 15, 13, 45, 30))

    def test_parse_time(self):
        self.assertEqual(parse_time('13:45'), time(13, 45))
        self.assertEqual(parse_time('13:45:30'), time(13, 45, 30))

    def test_parse_time_from_datetime(self):
        self.assertEqual(parse_time(datetime(2024, 3, 15, 13, 45)), time(13, 45))

    def test_parse_month_yields_first_of_month(self):
        self.assertEqual(parse_month('2024-03'), date(2024, 3, 1))

    def test_parse_month_from_date(self):
        self.assertEqual(parse_month(date(2024, 3, 15)), date(2024, 3, 1))

    def test_parse_week_yields_iso_monday(self):
        self.assertEqual(parse_week('2024-W11'), date(2024, 3, 11))
        self.assertEqual(parse_week('2024-W11').isoweekday(), 1)

    def test_parse_number(self):
        self.assertEqual(parse_number('42'), 42)
        self.assertIsInstance(parse_number('42'), int)
        self.assertEqual(parse_number('4.2'), 4.2)
        self.assertEqual(parse_number(7), 7)

    def test_parse_number_rejects_bool(self):
        """bool is an int subclass; a checkbox value is not a number."""
        with self.assertRaises(TypeError):
            parse_number(True)

    def test_parsers_raise_on_garbage(self):
        for parser in (parse_date, parse_datetime, parse_time, parse_month, parse_week, parse_number):
            with self.assertRaises((ValueError, TypeError), msg=parser.__name__):
                parser('not-a-value')


class TestParseInputValue(unittest.TestCase):
    """The dispatcher's contract: None, unparseable, and unregistered types."""

    def test_dispatches_by_input_type(self):
        self.assertEqual(parse_input_value('date', '2024-03-15'), date(2024, 3, 15))

    def test_none_value_yields_none(self):
        self.assertIsNone(parse_input_value('date', None))

    def test_unparseable_value_yields_none(self):
        self.assertIsNone(parse_input_value('date', 'not-a-date'))
        self.assertIsNone(parse_input_value('number', 'abc'))

    def test_unregistered_type_passes_value_through(self):
        self.assertEqual(parse_input_value('email', 'a@b.c'), 'a@b.c')
        self.assertEqual(parse_input_value('text', 'hi'), 'hi')
        self.assertEqual(parse_input_value('color', '#fff'), '#fff')

    def test_get_input_type_parser(self):
        self.assertIs(get_input_type_parser('date'), parse_date)
        self.assertIsNone(get_input_type_parser('email'))


class TestRegistry(unittest.TestCase):
    """The extension point, for input types SurveyJS gains later."""

    def setUp(self):
        # register_input_type mutates a module-level dict; restore it.
        self._snapshot = dict(INPUT_TYPE_PARSERS)
        self.addCleanup(lambda: (INPUT_TYPE_PARSERS.clear(),
                                 INPUT_TYPE_PARSERS.update(self._snapshot)))

    def test_register_new_input_type(self):
        register_input_type('duration', lambda v: timedelta(seconds=int(v)))
        form = make_form(
            {'elements': [{'type': 'text', 'name': 'x', 'inputType': 'duration'}]},
            {'x': '90'},
        )
        self.assertEqual(form.questions['x'].value, timedelta(seconds=90))

    def test_override_a_builtin(self):
        register_input_type('date', lambda v: 'overridden')
        self.assertEqual(parse_input_value('date', '2024-03-15'), 'overridden')

    def test_registered_parser_raising_yields_none(self):
        def boom(value):
            raise ValueError('nope')
        register_input_type('duration', boom)
        self.assertIsNone(parse_input_value('duration', '90'))

    def test_cleanup_restores_builtins(self):
        register_input_type('date', lambda v: 'overridden')
        self.doCleanups()
        self.assertIs(INPUT_TYPE_PARSERS['date'], parse_date)


class TestTextValueIsParsed(unittest.TestCase):

    def setUp(self):
        self.form = make_form(TYPED_SCHEMA, TYPED_DATA)

    def test_date(self):
        self.assertEqual(self.form.questions['d'].value, date(2024, 3, 15))

    def test_datetime_local(self):
        self.assertEqual(self.form.questions['dt'].value, datetime(2024, 3, 15, 13, 45))

    def test_time(self):
        self.assertEqual(self.form.questions['t'].value, time(13, 45))

    def test_month(self):
        self.assertEqual(self.form.questions['m'].value, date(2024, 3, 1))

    def test_week(self):
        self.assertEqual(self.form.questions['w'].value, date(2024, 3, 11))

    def test_number_and_range(self):
        self.assertEqual(self.form.questions['n'].value, 42)
        self.assertEqual(self.form.questions['r'].value, 4.2)

    def test_plain_text_passes_through(self):
        self.assertEqual(self.form.questions['plain'].value, 'hi')
        self.assertEqual(self.form.questions['mail'].value, 'a@b.c')

    def test_missing_value_yields_none(self):
        form = make_form(TYPED_SCHEMA, {})
        self.assertIsNone(form.questions['d'].value)

    def test_unparseable_value_yields_none(self):
        form = make_form(TYPED_SCHEMA, {'d': 'not-a-date'})
        self.assertIsNone(form.questions['d'].value)

    def test_default_value_is_parsed(self):
        form = make_form(
            {'elements': [{'type': 'text', 'name': 'd', 'inputType': 'date',
                           'defaultValue': '1999-12-31'}]},
            {},
        )
        self.assertEqual(form.questions['d'].value, date(1999, 12, 31))

    def test_value_on_the_creator_is_none(self):
        """A Creator element has no submitted value."""
        creator = SurveyCreator(TYPED_SCHEMA)
        self.assertIsNone(creator.questions['d'].value)


class TestTextToMethods(unittest.TestCase):
    """`to_*` parse as a named type regardless of the declared inputType."""

    def setUp(self):
        self.form = make_form(TYPED_SCHEMA, TYPED_DATA)

    def test_to_date(self):
        self.assertEqual(self.form.questions['d'].to_date(), date(2024, 3, 15))

    def test_to_datetime(self):
        self.assertEqual(self.form.questions['dt'].to_datetime(), datetime(2024, 3, 15, 13, 45))

    def test_to_time(self):
        self.assertEqual(self.form.questions['t'].to_time(), time(13, 45))

    def test_to_month(self):
        self.assertEqual(self.form.questions['m'].to_month(), date(2024, 3, 1))

    def test_to_week(self):
        self.assertEqual(self.form.questions['w'].to_week(), date(2024, 3, 11))

    def test_to_number(self):
        self.assertEqual(self.form.questions['n'].to_number(), 42)

    def test_to_date_narrows_a_datetime_value(self):
        """Regression: datetime subclasses date, so it used to pass through."""
        q = self.form.questions['d']
        q.raw_value = datetime(2024, 3, 15, 13, 45)
        self.assertNotIsInstance(q.to_date(), datetime)
        self.assertEqual(q.to_date(), date(2024, 3, 15))

    def test_to_date_on_garbage_yields_none(self):
        form = make_form(TYPED_SCHEMA, {'d': 'not-a-date'})
        self.assertIsNone(form.questions['d'].to_date())

    def test_to_date_on_missing_value_yields_none(self):
        form = make_form(TYPED_SCHEMA, {})
        self.assertIsNone(form.questions['d'].to_date())


class TestMultipleTextItemInputType(unittest.TestCase):
    """The schema from the request: a multipletext item with inputType date."""

    def setUp(self):
        self.form = make_form(
            {'elements': [
                {'type': 'multipletext', 'name': 'date 2', 'title': 'Date 2 multi',
                 'items': [
                     {'name': 'date', 'inputType': 'date'},
                     {'name': 'when', 'inputType': 'datetime-local', 'title': 'When'},
                     {'name': 'note'},
                 ]},
            ]},
            {'date 2': {'date': '2024-07-08', 'when': '2024-07-08T09:30', 'note': 'hi'}},
        )
        self.q = self.form.questions['date 2']

    def test_items_are_objects(self):
        self.assertEqual(len(self.q.items), 3)
        for item in self.q.items:
            self.assertIsInstance(item, MultipleTextItem)

    def test_item_names(self):
        self.assertEqual(self.q.item_names, ['date', 'when', 'note'])

    def test_item_input_type(self):
        self.assertEqual(self.q.get_item('date').input_type, 'date')
        self.assertEqual(self.q.get_item('when').input_type, 'datetime-local')

    def test_item_without_input_type_defaults_to_text(self):
        self.assertEqual(self.q.get_item('note').input_type, 'text')

    def test_item_value_parsed(self):
        self.assertEqual(self.q.get_item_value('date'), date(2024, 7, 8))
        self.assertEqual(self.q.get_item_value('when'), datetime(2024, 7, 8, 9, 30))

    def test_item_value_via_the_item(self):
        self.assertEqual(self.q.get_item('date').value, date(2024, 7, 8))

    def test_items_parse_independently_of_siblings(self):
        self.assertEqual(self.q.item_values, {
            'date': date(2024, 7, 8),
            'when': datetime(2024, 7, 8, 9, 30),
            'note': 'hi',
        })

    def test_raw_value_is_untouched(self):
        self.assertEqual(self.q.get_item_raw_value('date'), '2024-07-08')
        self.assertEqual(self.q.raw_value['date'], '2024-07-08')
        self.assertEqual(self.q.raw_item_values['date'], '2024-07-08')

    def test_item_raw_value(self):
        self.assertEqual(self.q.get_item('date').raw_value, '2024-07-08')

    def test_question_value_is_the_unparsed_dict(self):
        """The question declares no inputType; only its items do."""
        self.assertEqual(self.q.value, self.q.raw_value)

    def test_item_title_falls_back_to_name(self):
        self.assertEqual(self.q.get_item_title('when'), 'When')
        self.assertEqual(self.q.get_item_title('date'), 'date')

    def test_get_item_missing(self):
        self.assertIsNone(self.q.get_item('nope'))
        self.assertIsNone(self.q.get_item_value('nope'))
        self.assertEqual(self.q.get_item_title('nope'), 'nope')

    def test_missing_value_yields_none(self):
        form = make_form(
            {'elements': [{'type': 'multipletext', 'name': 'mt',
                           'items': [{'name': 'date', 'inputType': 'date'}]}]},
            {},
        )
        self.assertIsNone(form.questions['mt'].get_item_value('date'))

    def test_item_to_dict(self):
        self.assertEqual(self.q.get_item('date').to_dict(), {
            'name': 'date', 'title': 'date', 'inputType': 'date', 'value': '2024-07-08',
        })

    def test_item_repr(self):
        self.assertEqual(repr(self.q.get_item('date')), '<MultipleTextItem name=date>')


class TestValueContract(unittest.TestCase):
    """The invariants the raw_value/value split rests on."""

    def setUp(self):
        self.form = make_form(TYPED_SCHEMA, TYPED_DATA)
        self.q = self.form.questions['d']

    def test_value_is_read_only(self):
        """value is a derived view; assigning it would let a date into the
        slot that raw_value and to_dict() promise is JSON."""
        with self.assertRaises(AttributeError):
            self.q.value = '2024-01-01'

    def test_raw_value_is_the_settable_one(self):
        self.q.raw_value = '1999-12-31'
        self.assertEqual(self.q.raw_value, '1999-12-31')
        self.assertEqual(self.q.value, date(1999, 12, 31))

    def test_to_dict_emits_raw_value(self):
        self.assertEqual(self.q.to_dict()['value'], '2024-03-15')

    def test_to_dict_stays_json_serialisable(self):
        """A parsed value is a date, which json.dumps cannot encode."""
        self.assertIsInstance(self.q.value, date)
        json.dumps(self.q.to_dict())

    def test_every_element_to_dict_is_json_serialisable(self):
        for element in load_form().all_elements.values():
            json.dumps(element.to_dict())

    def test_multipletext_item_to_dict_emits_raw_value(self):
        form = make_form(
            {'elements': [{'type': 'multipletext', 'name': 'mt',
                           'items': [{'name': 'date', 'inputType': 'date'}]}]},
            {'mt': {'date': '2024-07-08'}},
        )
        item = form.questions['mt'].get_item('date')
        self.assertIsInstance(item.value, date)
        self.assertEqual(item.to_dict()['value'], '2024-07-08')
        json.dumps(item.to_dict())

    def test_raw_value_distinguishes_malformed_from_empty(self):
        malformed = make_form(TYPED_SCHEMA, {'d': '15/03/2024'}).questions['d']
        empty = make_form(TYPED_SCHEMA, {}).questions['d']
        self.assertIsNone(malformed.value)
        self.assertIsNone(empty.value)
        self.assertEqual(malformed.raw_value, '15/03/2024')
        self.assertIsNone(empty.raw_value)

    def test_default_value_reaches_raw_value(self):
        form = make_form(
            {'elements': [{'type': 'text', 'name': 'd', 'inputType': 'date',
                           'defaultValue': '1999-12-31'}]},
            {},
        )
        self.assertEqual(form.questions['d'].raw_value, '1999-12-31')
        self.assertEqual(form.questions['d'].value, date(1999, 12, 31))

    def test_form_get_value_and_get_raw_value(self):
        self.assertEqual(self.form.get_value('d'), date(2024, 3, 15))
        self.assertEqual(self.form.get_raw_value('d'), '2024-03-15')
        self.assertIsNone(self.form.get_value('nope'))
        self.assertIsNone(self.form.get_raw_value('nope'))


class TestValueComposesWithPanels(unittest.TestCase):
    """inputType parsing works on materialised paneldynamic rows."""

    def test_date_inside_a_panel_instance(self):
        form = make_form(
            {'elements': [{'type': 'paneldynamic', 'name': 'pd', 'templateElements': [
                {'type': 'text', 'name': 'when', 'inputType': 'date'},
            ]}]},
            {'pd': [{'when': '2024-01-02'}, {'when': '2025-06-07'}]},
        )
        panels = form.all_elements['pd'].panels
        self.assertEqual(panels[0]['when'].value, date(2024, 1, 2))
        self.assertEqual(panels[1]['when'].value, date(2025, 6, 7))

    def test_reachable_by_path(self):
        form = make_form(
            {'elements': [{'type': 'paneldynamic', 'name': 'pd', 'templateElements': [
                {'type': 'text', 'name': 'when', 'inputType': 'date'},
            ]}]},
            {'pd': [{'when': '2024-01-02'}]},
        )
        self.assertEqual(form.get_element_by_path('pd[0].when').value, date(2024, 1, 2))


if __name__ == '__main__':
    unittest.main()
