# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the Survey class."""

import unittest

from tests.utils import readjson, load_survey


class TestSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()

    def test_title(self):
        self.assertEqual(self.survey.title, 'Test Survey')

    def test_description(self):
        self.assertIn('comprehensive', self.survey.description)

    def test_pages(self):
        self.assertEqual(len(self.survey.pages), 5)

    def test_pages_names(self):
        names = [p['name'] for p in self.survey.pages]
        self.assertIn('page_basic_input', names)
        self.assertIn('page_choice', names)
        self.assertIn('page_special', names)
        self.assertIn('page_matrix', names)
        self.assertIn('page_layout', names)

    def test_questions_loaded(self):
        """All top-level and nested questions should be loaded."""
        self.assertGreater(len(self.survey.questions), 0)

    def test_input_questions(self):
        """Input questions should not include panel, html, image."""
        for name, q in self.survey.input_questions.items():
            self.assertTrue(q.is_input, f'{name} should be an input question')

    def test_non_input_questions_excluded(self):
        """Panel, html, image should not be in input_questions."""
        non_input = ['contactPanel', 'infoHtml', 'thankYouImage']
        for name in non_input:
            self.assertNotIn(name, self.survey.input_questions)

    def test_non_input_questions_in_questions(self):
        """Panel, html, image should still be in questions dict."""
        non_input = ['contactPanel', 'infoHtml', 'thankYouImage']
        for name in non_input:
            self.assertIn(name, self.survey.questions)

    def test_question_types(self):
        """Verify some expected question types."""
        self.assertEqual(self.survey.questions['firstName'].type, 'text')
        self.assertEqual(self.survey.questions['bio'].type, 'comment')
        self.assertEqual(self.survey.questions['favoriteColor'].type, 'radiogroup')
        self.assertEqual(self.survey.questions['hobbies'].type, 'checkbox')
        self.assertEqual(self.survey.questions['country'].type, 'dropdown')
        self.assertEqual(self.survey.questions['agreeTerms'].type, 'boolean')

    def test_nested_panel_questions(self):
        """Questions inside panels should be loaded."""
        self.assertIn('phone', self.survey.questions)
        self.assertIn('website', self.survey.questions)

    def test_survey_from_json_string(self):
        """Survey should accept a JSON string."""
        import json
        schema = readjson('test_survey_schema.json')
        from surveyjs_data import Survey
        survey = Survey(json.dumps(schema))
        self.assertEqual(survey.title, 'Test Survey')

    def test_get_question_class_unknown(self):
        """Unknown question types should fall back to base Question."""
        from surveyjs_data.questions.question import Question
        cls = self.survey.get_question_class({'type': 'unknowntype'})
        self.assertEqual(cls, Question)

    def test_form_property(self):
        """Survey's form property should be an empty dict."""
        self.assertEqual(self.survey.form, {})


if __name__ == '__main__':
    unittest.main()
