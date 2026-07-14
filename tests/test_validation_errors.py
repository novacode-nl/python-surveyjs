# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for validation errors on questions and forms."""

import unittest

from surveyjs import SurveyCreator, SurveyForm

SCHEMA = {
    'elements': [
        {'type': 'text', 'name': 'firstName', 'title': 'First name', 'isRequired': True},
        {'type': 'text', 'name': 'lastName', 'isRequired': True},
        {'type': 'text', 'name': 'nickname'},
        {'type': 'checkbox', 'name': 'colors', 'isRequired': True,
         'choices': ['red', 'green']},
        {'type': 'boolean', 'name': 'agree', 'isRequired': True},
        {'type': 'text', 'name': 'age', 'inputType': 'number', 'isRequired': True},
    ],
}


def build_form(data):
    return SurveyForm(data, creator=SurveyCreator(SCHEMA))


class TestQuestionValidationErrors(unittest.TestCase):

    def test_missing_required_reports_error(self):
        form = build_form({})
        errors = form.questions['firstName'].validation_errors()
        self.assertEqual(errors, {'required': 'First name is required'})

    def test_answered_required_has_no_error(self):
        form = build_form({'firstName': 'Alice'})
        self.assertEqual(form.questions['firstName'].validation_errors(), {})

    def test_optional_missing_has_no_error(self):
        form = build_form({})
        self.assertEqual(form.questions['nickname'].validation_errors(), {})

    def test_label_falls_back_to_name(self):
        """A required question with no title uses its name in the message."""
        form = build_form({})
        errors = form.questions['lastName'].validation_errors()
        self.assertEqual(errors, {'required': 'lastName is required'})

    def test_empty_choice_list_is_empty(self):
        form = build_form({'colors': []})
        self.assertEqual(
            form.questions['colors'].validation_errors(),
            {'required': 'colors is required'},
        )

    def test_answered_choice_list_has_no_error(self):
        form = build_form({'colors': ['red']})
        self.assertEqual(form.questions['colors'].validation_errors(), {})

    def test_false_boolean_is_an_answer(self):
        """False is a submitted answer, not emptiness."""
        form = build_form({'agree': False})
        self.assertEqual(form.questions['agree'].validation_errors(), {})

    def test_zero_number_is_an_answer(self):
        form = build_form({'age': 0})
        self.assertEqual(form.questions['age'].validation_errors(), {})

    def test_custom_required_error_text(self):
        creator = SurveyCreator({'elements': [
            {'type': 'text', 'name': 'firstName', 'title': 'First name',
             'isRequired': True, 'requiredErrorText': 'Please enter {{field}}!'},
        ]})
        form = SurveyForm({}, creator=creator)
        self.assertEqual(
            form.questions['firstName'].validation_errors(),
            {'required': 'Please enter First name!'},
        )

    def test_i18n_required_message(self):
        creator = SurveyCreator(
            {'elements': [
                {'type': 'text', 'name': 'firstName', 'title': 'First name',
                 'isRequired': True},
            ]},
            language='fr',
            i18n={'fr': {'{{field}} is required': '{{field}} est obligatoire'}},
        )
        form = SurveyForm({}, creator=creator, lang='fr')
        self.assertEqual(
            form.questions['firstName'].validation_errors(),
            {'required': 'First name est obligatoire'},
        )


class TestNumericValidator(unittest.TestCase):

    def _question(self, validator, data):
        schema = {'elements': [
            {'type': 'text', 'name': 'age', 'title': 'Age', 'inputType': 'number',
             'validators': [validator]},
        ]}
        form = SurveyForm(data, creator=SurveyCreator(schema))
        return form.questions['age']

    def test_below_min_with_both_bounds(self):
        q = self._question({'type': 'numeric', 'minValue': 18, 'maxValue': 99}, {'age': 5})
        self.assertEqual(
            q.validation_errors(),
            {'numeric': "The 'Age' should be at least 18 and at most 99"},
        )

    def test_above_max_with_both_bounds(self):
        q = self._question({'type': 'numeric', 'minValue': 18, 'maxValue': 99}, {'age': 150})
        self.assertEqual(
            q.validation_errors(),
            {'numeric': "The 'Age' should be at least 18 and at most 99"},
        )

    def test_below_min_only(self):
        q = self._question({'type': 'numeric', 'minValue': 18}, {'age': 5})
        self.assertEqual(q.validation_errors(), {'numeric': "The 'Age' should be at least 18"})

    def test_above_max_only(self):
        q = self._question({'type': 'numeric', 'maxValue': 99}, {'age': 150})
        self.assertEqual(q.validation_errors(), {'numeric': "The 'Age' should be at most 99"})

    def test_within_bounds_passes(self):
        q = self._question({'type': 'numeric', 'minValue': 18, 'maxValue': 99}, {'age': 30})
        self.assertEqual(q.validation_errors(), {})

    def test_bounds_are_inclusive(self):
        q = self._question({'type': 'numeric', 'minValue': 18, 'maxValue': 99}, {'age': 18})
        self.assertEqual(q.validation_errors(), {})

    def test_non_numeric_text(self):
        schema = {'elements': [
            {'type': 'text', 'name': 'age', 'title': 'Age', 'validators': [{'type': 'numeric'}]},
        ]}
        form = SurveyForm({'age': 'abc'}, creator=SurveyCreator(schema))
        self.assertEqual(
            form.questions['age'].validation_errors(),
            {'numeric': 'The value should be numeric.'},
        )


class TestTextValidator(unittest.TestCase):

    def _question(self, validator, value):
        schema = {'elements': [{'type': 'text', 'name': 'code', 'validators': [validator]}]}
        form = SurveyForm({'code': value}, creator=SurveyCreator(schema))
        return form.questions['code']

    def test_too_short_with_both_bounds(self):
        q = self._question({'type': 'text', 'minLength': 3, 'maxLength': 5}, 'ab')
        self.assertEqual(
            q.validation_errors(),
            {'text': 'Please enter at least 3 and no more than 5 characters.'},
        )

    def test_too_short_min_only(self):
        q = self._question({'type': 'text', 'minLength': 3}, 'ab')
        self.assertEqual(q.validation_errors(), {'text': 'Please enter at least 3 character(s).'})

    def test_too_long_max_only(self):
        q = self._question({'type': 'text', 'maxLength': 5}, 'abcdef')
        self.assertEqual(q.validation_errors(), {'text': 'Please enter no more than 5 character(s).'})

    def test_within_length_passes(self):
        q = self._question({'type': 'text', 'minLength': 3, 'maxLength': 5}, 'abcd')
        self.assertEqual(q.validation_errors(), {})

    def test_no_digits_allowed(self):
        q = self._question({'type': 'text', 'allowDigits': False}, 'ab3')
        self.assertEqual(q.validation_errors(), {'text': 'Numbers are not allowed.'})

    def test_no_digits_passes_when_clean(self):
        q = self._question({'type': 'text', 'allowDigits': False}, 'abc')
        self.assertEqual(q.validation_errors(), {})


class TestAnswerCountValidator(unittest.TestCase):

    def _question(self, validator, value):
        schema = {'elements': [
            {'type': 'checkbox', 'name': 'colors', 'choices': ['a', 'b', 'c'],
             'validators': [validator]},
        ]}
        form = SurveyForm({'colors': value}, creator=SurveyCreator(schema))
        return form.questions['colors']

    def test_too_few(self):
        q = self._question({'type': 'answercount', 'minCount': 2}, ['a'])
        self.assertEqual(q.validation_errors(), {'answercount': 'Please select at least 2 option(s).'})

    def test_too_many(self):
        q = self._question({'type': 'answercount', 'maxCount': 2}, ['a', 'b', 'c'])
        self.assertEqual(q.validation_errors(), {'answercount': 'Please select no more than 2 option(s).'})

    def test_within_count_passes(self):
        q = self._question({'type': 'answercount', 'minCount': 1, 'maxCount': 2}, ['a', 'b'])
        self.assertEqual(q.validation_errors(), {})

    def test_empty_selection_defers_to_required(self):
        """An empty selection is the required check's concern, not answercount's."""
        q = self._question({'type': 'answercount', 'minCount': 2}, [])
        self.assertEqual(q.validation_errors(), {})


class TestRegexValidator(unittest.TestCase):

    def _question(self, validator, value):
        schema = {'elements': [{'type': 'text', 'name': 'zip', 'validators': [validator]}]}
        form = SurveyForm({'zip': value}, creator=SurveyCreator(schema))
        return form.questions['zip']

    def test_mismatch_uses_custom_text(self):
        q = self._question(
            {'type': 'regex', 'regex': '^[0-9]{4}[A-Z]{2}$', 'text': 'Not a valid zip.'},
            '99999',
        )
        self.assertEqual(q.validation_errors(), {'regex': 'Not a valid zip.'})

    def test_match_passes(self):
        q = self._question({'type': 'regex', 'regex': '^[0-9]{4}[A-Z]{2}$'}, '1234AB')
        self.assertEqual(q.validation_errors(), {})

    def test_default_message_when_no_text(self):
        q = self._question({'type': 'regex', 'regex': '^[0-9]+$'}, 'abc')
        self.assertEqual(
            q.validation_errors(),
            {'regex': 'Entered value does not match the expected pattern.'},
        )

    def test_case_insensitive(self):
        q = self._question({'type': 'regex', 'regex': '^abc$', 'caseInsensitive': True}, 'ABC')
        self.assertEqual(q.validation_errors(), {})

    def test_invalid_pattern_is_ignored(self):
        """An un-compilable pattern is treated as no constraint, not a crash."""
        q = self._question({'type': 'regex', 'regex': '([', 'text': 'x'}, 'anything')
        self.assertEqual(q.validation_errors(), {})


class TestEmailValidator(unittest.TestCase):

    def _question(self, value):
        schema = {'elements': [
            {'type': 'text', 'name': 'email', 'inputType': 'email',
             'validators': [{'type': 'email'}]},
        ]}
        form = SurveyForm({'email': value}, creator=SurveyCreator(schema))
        return form.questions['email']

    def test_invalid_email(self):
        self.assertEqual(
            self._question('not-an-email').validation_errors(),
            {'email': 'Please enter a valid e-mail address.'},
        )

    def test_valid_email(self):
        self.assertEqual(self._question('alice@example.com').validation_errors(), {})


class TestValidatorEdgeCases(unittest.TestCase):

    def test_unknown_validator_type_is_skipped(self):
        schema = {'elements': [
            {'type': 'text', 'name': 'x', 'validators': [{'type': 'expression', 'expression': '1=1'}]},
        ]}
        form = SurveyForm({'x': 'value'}, creator=SurveyCreator(schema))
        self.assertEqual(form.questions['x'].validation_errors(), {})

    def test_validators_skipped_on_empty_value(self):
        """Validators pass on empty input; only required fires there."""
        schema = {'elements': [
            {'type': 'text', 'name': 'age', 'inputType': 'number',
             'validators': [{'type': 'numeric', 'minValue': 18}]},
        ]}
        form = SurveyForm({}, creator=SurveyCreator(schema))
        self.assertEqual(form.questions['age'].validation_errors(), {})

    def test_custom_validator_text_overrides_default(self):
        schema = {'elements': [
            {'type': 'text', 'name': 'age', 'inputType': 'number',
             'validators': [{'type': 'numeric', 'minValue': 18, 'text': 'Too young!'}]},
        ]}
        form = SurveyForm({'age': 5}, creator=SurveyCreator(schema))
        self.assertEqual(form.questions['age'].validation_errors(), {'numeric': 'Too young!'})

    def test_required_and_validator_do_not_collide(self):
        """A required, empty field reports only 'required' — validators sit out."""
        schema = {'elements': [
            {'type': 'text', 'name': 'age', 'title': 'Age', 'inputType': 'number',
             'isRequired': True, 'validators': [{'type': 'numeric', 'minValue': 18}]},
        ]}
        form = SurveyForm({}, creator=SurveyCreator(schema))
        self.assertEqual(
            form.questions['age'].validation_errors(),
            {'required': 'Age is required'},
        )


class TestFormValidationErrors(unittest.TestCase):

    def test_aggregates_errors_by_question_name(self):
        form = build_form({'firstName': 'Alice', 'colors': [], 'agree': False, 'age': 5})
        errors = form.validation_errors()
        self.assertEqual(errors, {
            'lastName': {'required': 'lastName is required'},
            'colors': {'required': 'colors is required'},
        })

    def test_aggregates_required_and_validator_errors(self):
        schema = {'elements': [
            {'type': 'text', 'name': 'firstName', 'title': 'First name', 'isRequired': True},
            {'type': 'text', 'name': 'age', 'title': 'Age', 'inputType': 'number',
             'validators': [{'type': 'numeric', 'minValue': 18}]},
        ]}
        form = SurveyForm({'age': 5}, creator=SurveyCreator(schema))
        self.assertEqual(form.validation_errors(), {
            'firstName': {'required': 'First name is required'},
            'age': {'numeric': "The 'Age' should be at least 18"},
        })

    def test_valid_submission_has_no_errors(self):
        form = build_form({
            'firstName': 'Alice',
            'lastName': 'Smith',
            'colors': ['red'],
            'agree': True,
            'age': 30,
        })
        self.assertEqual(form.validation_errors(), {})

    def test_returns_plain_dict(self):
        """Result is a plain dict — reading an absent key raises, and does not
        silently insert an empty entry."""
        form = build_form({'firstName': 'Alice', 'lastName': 'Smith',
                           'colors': ['red'], 'agree': True, 'age': 30})
        errors = form.validation_errors()
        self.assertNotIsInstance(errors, __import__('collections').defaultdict)
        self.assertNotIn('nickname', errors)


if __name__ == '__main__':
    unittest.main()
