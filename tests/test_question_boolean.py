# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the boolean question type."""

import unittest

from surveyjs import SurveyCreator, SurveyForm
from surveyjs.elements.boolean import QuestionBoolean
from surveyjs.elements.inputtype import parse_boolean, parse_input_value
from tests.utils import load_creator, load_form


class TestQuestionBoolean(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()
        self.q = self.survey.questions['agreeTerms']

    def test_class_type(self):
        self.assertIsInstance(self.q, QuestionBoolean)

    def test_type(self):
        self.assertEqual(self.q.type, 'boolean')

    def test_title(self):
        self.assertEqual(self.q.title, 'I agree to the Terms of Service')

    def test_label_true(self):
        self.assertEqual(self.q.label_true, 'Yes')

    def test_label_false(self):
        self.assertEqual(self.q.label_false, 'No')

    def test_value_true(self):
        self.assertEqual(self.q.value_true, 'agreed')

    def test_value_false(self):
        self.assertEqual(self.q.value_false, 'declined')

    def test_render_as(self):
        self.assertEqual(self.q.render_as, 'checkbox')

    def test_no_input_type(self):
        """SurveyJS booleans carry no inputType; the class types `value` itself."""
        self.assertEqual(self.q.input_type, '')


class TestBooleanForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.questions['agreeTerms']

    def test_raw_value(self):
        self.assertEqual(self.q.raw_value, 'agreed')

    def test_value_custom_true(self):
        self.assertIs(self.q.value, True)

    def test_to_bool_custom_true(self):
        self.assertIs(self.q.to_bool(), True)

    def test_value_text(self):
        self.assertEqual(self.q.value_text, 'Yes')


class TestParseBoolean(unittest.TestCase):

    def test_bools_pass_through(self):
        self.assertIs(parse_boolean(True), True)
        self.assertIs(parse_boolean(False), False)

    def test_strings(self):
        for text in ('true', 'True', ' yes ', 'on', '1'):
            self.assertIs(parse_boolean(text), True, text)
        for text in ('false', 'FALSE', 'no', 'off', '0'):
            self.assertIs(parse_boolean(text), False, text)

    def test_numbers(self):
        self.assertIs(parse_boolean(1), True)
        self.assertIs(parse_boolean(0), False)

    def test_custom_values(self):
        self.assertIs(parse_boolean('agreed', 'agreed', 'declined'), True)
        self.assertIs(parse_boolean('declined', 'agreed', 'declined'), False)

    def test_unrecognised_raises(self):
        with self.assertRaises(ValueError):
            parse_boolean('maybe')

    def test_registered_for_boolean_input_type(self):
        self.assertIs(parse_input_value('boolean', 'true'), True)
        self.assertIsNone(parse_input_value('boolean', 'maybe'))


class TestBooleanValue(unittest.TestCase):

    def make_question(self, raw_value, **schema):
        element = dict({'type': 'boolean', 'name': 'b'}, **schema)
        data = {} if raw_value is None else {'b': raw_value}
        form = SurveyForm(data, creator=SurveyCreator({'elements': [element]}))
        return form.questions['b']

    def test_true_false(self):
        self.assertIs(self.make_question(True).value, True)
        self.assertIs(self.make_question(False).value, False)

    def test_custom_false(self):
        q = self.make_question('declined', valueTrue='agreed', valueFalse='declined')
        self.assertIs(q.value, False)

    def test_unanswered_is_none(self):
        self.assertIsNone(self.make_question(None).value)

    def test_value_text_false(self):
        self.assertEqual(self.make_question(False).value_text, 'No')

    def test_value_text_custom_labels(self):
        q = self.make_question('declined', valueTrue='agreed', valueFalse='declined',
                               labelTrue='I agree', labelFalse='I decline')
        self.assertEqual(q.value_text, 'I decline')

    def test_value_text_unanswered_is_none(self):
        self.assertIsNone(self.make_question(None).value_text)
        self.assertIsNone(self.make_question('maybe').value_text)

    def test_default_value(self):
        self.assertIs(self.make_question(None, defaultValue=True).value, True)

    def test_unrecognised_is_none(self):
        q = self.make_question('maybe')
        self.assertIsNone(q.value)
        self.assertEqual(q.raw_value, 'maybe')


if __name__ == '__main__':
    unittest.main()
