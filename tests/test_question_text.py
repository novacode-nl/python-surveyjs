# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the text question type."""

import unittest
from datetime import date, datetime

from tests.utils import load_survey, load_form


class TestTextSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()

    def test_class_type(self):
        from surveyjs_data.questions.text import textQuestion
        q = self.survey.questions['firstName']
        self.assertIsInstance(q, textQuestion)

    def test_name(self):
        self.assertEqual(self.survey.questions['firstName'].name, 'firstName')

    def test_title(self):
        self.assertEqual(self.survey.questions['firstName'].title, 'First Name')

    def test_type(self):
        self.assertEqual(self.survey.questions['firstName'].type, 'text')

    def test_description(self):
        self.assertEqual(
            self.survey.questions['firstName'].description,
            'Enter your first name'
        )

    def test_is_required(self):
        self.assertTrue(self.survey.questions['firstName'].is_required)

    def test_placeholder(self):
        self.assertEqual(self.survey.questions['firstName'].placeholder, 'John')

    def test_input_type_text(self):
        self.assertEqual(self.survey.questions['firstName'].input_type, 'text')

    def test_input_type_number(self):
        self.assertEqual(self.survey.questions['age'].input_type, 'number')

    def test_input_type_date(self):
        self.assertEqual(self.survey.questions['birthDate'].input_type, 'date')

    def test_input_type_email(self):
        self.assertEqual(self.survey.questions['email'].input_type, 'email')

    def test_max_length(self):
        self.assertEqual(self.survey.questions['email'].max_length, 100)

    def test_min_max_step(self):
        q = self.survey.questions['age']
        self.assertEqual(q.min, 0)
        self.assertEqual(q.max, 150)
        self.assertEqual(q.step, 1)

    def test_validators(self):
        q = self.survey.questions['email']
        self.assertEqual(len(q.validators), 1)
        self.assertEqual(q.validators[0]['type'], 'email')

    def test_is_input(self):
        self.assertTrue(self.survey.questions['firstName'].is_input)

    def test_default_value_none(self):
        """Survey-level text questions normally have no value."""
        self.assertIsNone(self.survey.questions['firstName'].value)


class TestTextForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_value_string(self):
        self.assertEqual(self.form.input_questions['firstName'].value, 'Alice')

    def test_value_number(self):
        self.assertEqual(self.form.input_questions['age'].value, 30)

    def test_value_email(self):
        self.assertEqual(
            self.form.input_questions['email'].value, 'alice@example.com'
        )

    def test_to_number(self):
        q = self.form.input_questions['age']
        self.assertEqual(q.to_number(), 30)

    def test_to_number_none(self):
        """to_number on a text (non-number) field returns None if not numeric."""
        q = self.form.input_questions['firstName']
        self.assertIsNone(q.to_number())

    def test_to_date(self):
        q = self.form.input_questions['birthDate']
        result = q.to_date()
        self.assertIsInstance(result, date)
        self.assertEqual(result, date(1993, 5, 15))

    def test_to_datetime(self):
        q = self.form.input_questions['appointmentTime']
        result = q.to_datetime()
        self.assertIsInstance(result, datetime)
        self.assertEqual(result, datetime(2024, 6, 15, 10, 30))

    def test_to_dict(self):
        q = self.form.input_questions['firstName']
        d = q.to_dict()
        self.assertEqual(d['name'], 'firstName')
        self.assertEqual(d['value'], 'Alice')
        self.assertEqual(d['type'], 'text')


if __name__ == '__main__':
    unittest.main()
