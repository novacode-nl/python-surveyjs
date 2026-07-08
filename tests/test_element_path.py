# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for element `path` and `input_path`."""

import unittest

from surveyjs import SurveyCreator
from tests.utils import load_creator, load_form, readjson

COLLIDING_SCHEMA = {
    'elements': [
        {'type': 'paneldynamic', 'name': 'jobs',
         'templateElements': [{'type': 'text', 'name': 'year'}]},
        {'type': 'paneldynamic', 'name': 'school',
         'templateElements': [{'type': 'text', 'name': 'year'}]},
    ],
}


class TestElementIdIsGone(unittest.TestCase):
    """SurveyJS identifies elements by `name` and never serialises an `id`, so
    the library models no id at all — `path` is the stable, unique handle."""

    def setUp(self):
        self.survey = load_creator()
        self.form = load_form()

    def test_elements_have_no_id_attribute(self):
        element = self.survey.questions['firstName']
        self.assertFalse(hasattr(element, 'id'))

    def test_owners_have_no_id_registries(self):
        for owner in (self.survey, self.form):
            self.assertFalse(hasattr(owner, 'all_element_ids'))
            self.assertFalse(hasattr(owner, 'all_component_ids'))

    def test_an_authored_id_is_ignored_but_left_in_raw(self):
        creator = SurveyCreator({'elements': [{'type': 'text', 'name': 'a', 'id': 'my-id'}]})
        element = creator.questions['a']
        self.assertFalse(hasattr(element, 'id'))
        self.assertEqual(element.raw['id'], 'my-id')
        self.assertEqual(element.path_str, 'a')


class TestElementPath(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()

    def test_root_element_path(self):
        self.assertEqual(self.survey.questions['age'].path, ['age'])
        self.assertEqual(self.survey.questions['age'].path_str, 'age')

    def test_nested_element_path_includes_container(self):
        phone = self.survey.all_elements['phone']
        self.assertEqual(phone.path, ['contactPanel', 'phone'])
        self.assertEqual(phone.path_str, 'contactPanel.phone')

    def test_path_is_stable_across_parses(self):
        other = load_creator()
        self.assertEqual(
            self.survey.all_elements['phone'].path_str,
            other.all_elements['phone'].path_str,
        )

    def test_path_matches_between_creator_and_form(self):
        form = load_form()
        for name, element in form.all_elements.items():
            self.assertEqual(element.path_str, self.survey.all_elements[name].path_str)

    def test_every_element_registered_by_path(self):
        for element in self.survey.all_elements.values():
            self.assertIs(self.survey.all_element_paths[element.path_str], element)

    def test_get_element_by_path_dotted(self):
        element = self.survey.get_element_by_path('contactPanel.phone')
        self.assertIs(element, self.survey.all_elements['phone'])

    def test_get_element_by_path_list(self):
        element = self.survey.get_element_by_path(['contactPanel', 'phone'])
        self.assertIs(element, self.survey.all_elements['phone'])

    def test_get_element_by_path_missing(self):
        self.assertIsNone(self.survey.get_element_by_path('nope.nope'))

    def test_all_component_paths_alias(self):
        self.assertIs(self.survey.all_component_paths, self.survey.all_element_paths)


class TestPathDisambiguatesCollidingNames(unittest.TestCase):
    """Template children of two paneldynamics may share a name."""

    def setUp(self):
        self.survey = SurveyCreator(COLLIDING_SCHEMA)

    def test_name_registry_is_lossy(self):
        # Documents existing behaviour: the second 'year' wins.
        self.assertEqual(list(self.survey.all_elements), ['jobs', 'year', 'school'])

    def test_path_registry_is_lossless(self):
        self.assertEqual(
            list(self.survey.all_element_paths),
            ['jobs', 'jobs.year', 'school', 'school.year'],
        )

    def test_colliding_elements_are_distinct(self):
        jobs_year = self.survey.get_element_by_path('jobs.year')
        school_year = self.survey.get_element_by_path('school.year')
        self.assertIsNot(jobs_year, school_year)
        self.assertEqual(jobs_year.parent.name, 'jobs')
        self.assertEqual(school_year.parent.name, 'school')


class TestInputPath(unittest.TestCase):
    """`input_path` is the path to a value in the submission data."""

    def setUp(self):
        self.survey = load_creator()

    def test_root_question(self):
        self.assertEqual(self.survey.questions['age'].input_path, ['age'])

    def test_panel_is_transparent(self):
        """A panel groups visually but adds no data nesting level."""
        phone = self.survey.all_elements['phone']
        self.assertEqual(phone.path, ['contactPanel', 'phone'])
        self.assertEqual(phone.input_path, ['phone'])
        self.assertEqual(phone.input_path_str, 'phone')

    def test_paneldynamic_nests(self):
        year = self.survey.get_element_by_path('education.year')
        self.assertEqual(year.input_path, ['education', 'year'])
        self.assertEqual(year.input_path_str, 'education.year')

    def test_panel_inside_paneldynamic(self):
        """The paneldynamic contributes a level; the inner panel does not."""
        creator = SurveyCreator({'elements': [
            {'type': 'paneldynamic', 'name': 'pd', 'templateElements': [
                {'type': 'panel', 'name': 'grp', 'elements': [{'type': 'text', 'name': 'x'}]},
            ]},
        ]})
        x = creator.all_elements['x']
        self.assertEqual(x.path, ['pd', 'grp', 'x'])
        self.assertEqual(x.input_path, ['pd', 'x'])

    def test_nests_data_flags(self):
        self.assertFalse(self.survey.questions['age'].nests_data)
        self.assertFalse(self.survey.all_elements['contactPanel'].nests_data)
        self.assertTrue(self.survey.all_elements['education'].nests_data)

    def test_input_path_resolves_against_submission_data(self):
        """The whole point: input_path must actually index the data."""
        data = readjson('test_survey_form.json')

        phone = self.survey.all_elements['phone']
        self.assertEqual(data[phone.input_path[0]], '+1-555-0123')

        panel, field = self.survey.get_element_by_path('education.year').input_path
        self.assertEqual([row[field] for row in data[panel]], [2015, 2017])


class TestFormPaths(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_every_element_registered_by_path(self):
        for element in self.form.all_elements.values():
            self.assertIs(self.form.all_element_paths[element.path_str], element)

    def test_get_element_by_path_returns_form_element_with_value(self):
        phone = self.form.get_element_by_path('contactPanel.phone')
        self.assertEqual(phone.value, '+1-555-0123')
        self.assertIsNot(phone, self.form.creator.all_elements['phone'])

    def test_get_element_by_path_list(self):
        self.assertIs(
            self.form.get_element_by_path(['contactPanel', 'phone']),
            self.form.all_elements['phone'],
        )

    def test_get_element_by_path_missing(self):
        self.assertIsNone(self.form.get_element_by_path('nope'))

    def test_path_correlates_form_element_to_creator_element(self):
        """The thing a random uuid id could never do."""
        form_phone = self.form.all_elements['phone']
        creator_phone = self.form.creator.get_element_by_path(form_phone.path_str)
        self.assertIsNotNone(creator_phone)
        self.assertEqual(creator_phone.name, 'phone')

    def test_all_component_paths_alias(self):
        self.assertIs(self.form.all_component_paths, self.form.all_element_paths)


if __name__ == '__main__':
    unittest.main()
