# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the Form class."""

import json
import unittest

from surveyjs import SurveyForm
from tests.utils import load_form, load_creator, readjson, readfile


class TestForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_form_questions_loaded(self):
        self.assertGreater(len(self.form.elements), 0)

    def test_form_questions(self):
        self.assertGreater(len(self.form.questions), 0)

    def test_form_data_accessor(self):
        """form.data.firstName should return the question object."""
        q = self.form.data.firstName
        self.assertIsNotNone(q)
        self.assertEqual(q.value, 'Alice')

    def test_form_data_accessor_nonexistent(self):
        """Accessing a nonexistent question via data returns None."""
        self.assertIsNone(self.form.data.nonExistentQuestion)

    def test_get_question_by_name(self):
        q = self.form.get_question_by_name('firstName')
        self.assertIsNotNone(q)
        self.assertEqual(q.name, 'firstName')

    def test_get_value(self):
        self.assertEqual(self.form.get_value('firstName'), 'Alice')
        self.assertEqual(self.form.get_value('age'), 30)

    def test_get_value_nonexistent(self):
        self.assertIsNone(self.form.get_value('nonExistent'))

    def test_form_from_survey_schema_json(self):
        """Form can be created with creator_schema_json instead of creator."""
        schema = readfile('test_survey_schema.json')
        form_json = readjson('test_survey_form.json')
        form = SurveyForm(form_json, creator_schema_json=schema)
        self.assertEqual(form.get_value('firstName'), 'Alice')

    def test_form_constructor_both_raises(self):
        """Providing both survey and survey_schema_json should raise."""
        schema = readjson('test_survey_schema.json')
        form_data = readjson('test_survey_form.json')
        creator = load_creator()
        with self.assertRaises(Exception):
            SurveyForm(form_data, creator=creator, creator_schema_json=schema)

    def test_form_constructor_neither_raises(self):
        """Providing neither survey nor survey_schema_json should raise."""
        form_data = readjson('test_survey_form.json')
        with self.assertRaises(Exception):
            SurveyForm(form_data)

    def test_form_from_json_string(self):
        """Form should accept a JSON string for form_json."""

        form_json = readjson('test_survey_form.json')
        creator = load_creator()
        form = SurveyForm(json.dumps(form_json), creator=creator)
        self.assertEqual(form.get_value('firstName'), 'Alice')

    def test_form_all_input_values_loaded(self):
        """All submitted values should be accessible."""
        expected = {
            'firstName': 'Alice',
            'age': 30,
            'country': 'us',
            'satisfaction': 8,
        }
        for name, expected_val in expected.items():
            self.assertEqual(
                self.form.get_value(name), expected_val,
                f"Value mismatch for {name}"
            )

    def test_non_input_not_in_questions(self):
        """Panel, html, image should not be in input_questions."""
        non_input = ['contactPanel', 'infoHtml', 'thankYouImage']
        for name in non_input:
            self.assertNotIn(name, self.form.questions)


if __name__ == '__main__':
    unittest.main()
