# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

"""Tests for the file question type."""

import unittest

from tests.utils import load_survey, load_form


class TestFileSurvey(unittest.TestCase):

    def setUp(self):
        self.survey = load_survey()
        self.q = self.survey.questions['resume']

    def test_class_type(self):
        from surveyjs_data.questions.file import fileQuestion
        self.assertIsInstance(self.q, fileQuestion)

    def test_type(self):
        self.assertEqual(self.q.type, 'file')

    def test_title(self):
        self.assertEqual(self.q.title, 'Upload Resume')

    def test_store_data_as_text(self):
        self.assertTrue(self.q.store_data_as_text)

    def test_allow_multiple(self):
        self.assertTrue(self.q.allow_multiple)

    def test_max_size(self):
        self.assertEqual(self.q.max_size, 5242880)

    def test_accepted_types(self):
        self.assertEqual(self.q.accepted_types, '.pdf,.doc,.docx')


class TestFileForm(unittest.TestCase):

    def setUp(self):
        self.form = load_form()
        self.q = self.form.input_questions['resume']

    def test_value_is_list(self):
        self.assertIsInstance(self.q.value, list)

    def test_files(self):
        files = self.q.files
        self.assertEqual(len(files), 2)

    def test_file_count(self):
        self.assertEqual(self.q.file_count, 2)

    def test_file_names(self):
        files = self.q.files
        names = [f['name'] for f in files]
        self.assertIn('resume.pdf', names)
        self.assertIn('cover_letter.docx', names)

    def test_file_types(self):
        files = self.q.files
        types = [f['type'] for f in files]
        self.assertIn('application/pdf', types)


if __name__ == '__main__':
    unittest.main()
