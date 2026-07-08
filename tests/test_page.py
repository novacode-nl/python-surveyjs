# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the Page class and page/element back-references."""

import unittest

from surveyjs import SurveyCreator, SurveyForm
from tests.utils import load_creator, load_form

PAGE_NAMES = [
    'page_basic_input',
    'page_choice',
    'page_special',
    'page_matrix',
    'page_layout',
]

FLAT_SCHEMA = {
    'title': 'Flat Survey',
    'elements': [
        {'type': 'text', 'name': 'firstName'},
        {'type': 'text', 'name': 'lastName'},
    ],
}


class TestCreatorPages(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()

    def test_pages_are_page_objects(self):
        from surveyjs.page import Page
        self.assertEqual(len(self.survey.pages), 5)
        for page in self.survey.pages:
            self.assertIsInstance(page, Page)

    def test_pages_in_schema_order(self):
        self.assertEqual([p.name for p in self.survey.pages], PAGE_NAMES)

    def test_page_index(self):
        for index, page in enumerate(self.survey.pages):
            self.assertEqual(page.index, index)

    def test_page_title(self):
        self.assertEqual(self.survey.pages[0].title, 'Basic Input')

    def test_page_title_falls_back_to_name(self):
        creator = SurveyCreator({'pages': [{'name': 'p1', 'elements': []}]})
        self.assertEqual(creator.pages[0].title, 'p1')

    def test_page_is_not_implicit(self):
        for page in self.survey.pages:
            self.assertFalse(page.implicit)

    def test_get_page_by_name(self):
        page = self.survey.get_page_by_name('page_choice')
        self.assertIsNotNone(page)
        self.assertEqual(page.name, 'page_choice')

    def test_get_page_by_name_missing(self):
        self.assertIsNone(self.survey.get_page_by_name('nope'))

    def test_page_elements_are_root_elements(self):
        """A page holds only root elements, never nested children."""
        for page in self.survey.pages:
            for element in page.elements.values():
                self.assertIsNone(element.parent)

    def test_pages_partition_root_elements(self):
        """Every root element belongs to exactly one page, in order."""
        from_pages = [n for p in self.survey.pages for n in p.elements]
        self.assertEqual(from_pages, list(self.survey.elements))

    def test_page_elements_are_the_same_objects(self):
        page = self.survey.get_page_by_name('page_basic_input')
        self.assertIs(page.elements['firstName'], self.survey.elements['firstName'])

    def test_page_questions_excludes_layout(self):
        page = self.survey.get_page_by_name('page_layout')
        self.assertIn('contactPanel', page.elements)
        self.assertNotIn('contactPanel', page.questions)

    def test_pages_are_not_elements(self):
        """Pages must not leak into the element registries."""
        for name in PAGE_NAMES:
            self.assertNotIn(name, self.survey.all_elements)
            self.assertNotIn(name, self.survey.elements)
            self.assertNotIn(name, self.survey.questions)

    def test_page_to_dict(self):
        page = self.survey.get_page_by_name('page_basic_input')
        data = page.to_dict()
        self.assertEqual(data['name'], 'page_basic_input')
        self.assertEqual(data['title'], 'Basic Input')
        self.assertEqual(len(data['elements']), len(page.elements))

    def test_page_repr(self):
        self.assertEqual(repr(self.survey.pages[0]), '<Page name=page_basic_input>')


class TestCreatorElementPage(unittest.TestCase):

    def setUp(self):
        self.survey = load_creator()

    def test_root_element_page(self):
        self.assertEqual(self.survey.questions['firstName'].page.name, 'page_basic_input')

    def test_nested_element_inherits_page_from_parent(self):
        phone = self.survey.all_elements['phone']
        self.assertIsNotNone(phone.parent)
        self.assertIs(phone.page, phone.parent.page)
        self.assertEqual(phone.page.name, 'page_layout')

    def test_every_element_has_a_page(self):
        for element in self.survey.all_elements.values():
            self.assertIsNotNone(element.page, f'{element.name} has no page')


class TestImplicitPage(unittest.TestCase):
    """A pages-less schema is represented by one implicit page."""

    def setUp(self):
        self.survey = SurveyCreator(FLAT_SCHEMA)

    def test_single_implicit_page(self):
        self.assertEqual(len(self.survey.pages), 1)
        self.assertTrue(self.survey.pages[0].implicit)

    def test_implicit_page_name(self):
        self.assertEqual(self.survey.pages[0].name, 'page1')

    def test_implicit_page_holds_top_level_elements(self):
        self.assertEqual(list(self.survey.pages[0].elements), ['firstName', 'lastName'])

    def test_element_page(self):
        self.assertEqual(self.survey.questions['firstName'].page.name, 'page1')

    def test_empty_schema_has_one_empty_page(self):
        survey = SurveyCreator({})
        self.assertEqual(len(survey.pages), 1)
        self.assertEqual(len(survey.pages[0].elements), 0)

    def test_form_mirrors_implicit_page(self):
        form = SurveyForm({'firstName': 'Bob'}, creator=self.survey)
        self.assertEqual([p.name for p in form.pages], ['page1'])
        self.assertEqual(form.questions['firstName'].page.name, 'page1')


class TestFormPages(unittest.TestCase):

    def setUp(self):
        self.form = load_form()

    def test_pages_mirror_creator(self):
        self.assertEqual([p.name for p in self.form.pages], PAGE_NAMES)
        self.assertEqual(
            [p.index for p in self.form.pages],
            [p.index for p in self.form.creator.pages],
        )

    def test_page_owner_is_the_form(self):
        for page in self.form.pages:
            self.assertIs(page.owner, self.form)

    def test_page_holds_form_elements_not_creator_elements(self):
        page = self.form.get_page_by_name('page_basic_input')
        self.assertIs(page.elements['firstName'], self.form.elements['firstName'])
        self.assertIsNot(
            page.elements['firstName'],
            self.form.creator.elements['firstName'],
        )

    def test_pages_partition_root_elements(self):
        from_pages = [n for p in self.form.pages for n in p.elements]
        self.assertEqual(from_pages, list(self.form.elements))

    def test_page_elements_carry_values(self):
        page = self.form.get_page_by_name('page_basic_input')
        self.assertEqual(page.elements['firstName'].value, 'Alice')

    def test_get_page_by_name(self):
        self.assertEqual(self.form.get_page_by_name('page_matrix').name, 'page_matrix')

    def test_get_page_by_name_missing(self):
        self.assertIsNone(self.form.get_page_by_name('nope'))

    def test_root_element_page(self):
        self.assertEqual(self.form.questions['firstName'].page.name, 'page_basic_input')

    def test_nested_element_inherits_page(self):
        phone = self.form.all_elements['phone']
        self.assertIsNotNone(phone.parent)
        self.assertEqual(phone.page.name, 'page_layout')

    def test_every_element_has_a_page(self):
        for element in self.form.all_elements.values():
            self.assertIsNotNone(element.page, f'{element.name} has no page')

    def test_pages_are_not_elements(self):
        for name in PAGE_NAMES:
            self.assertNotIn(name, self.form.all_elements)
            self.assertNotIn(name, self.form.questions)


class TestPageProperties(unittest.TestCase):

    def test_optional_properties(self):
        creator = SurveyCreator({
            'pages': [{
                'name': 'p1',
                'title': 'Page One',
                'description': 'Some help',
                'visibleIf': '{age} > 18',
                'visible': False,
                'readOnly': True,
                'elements': [],
            }],
        })
        page = creator.pages[0]
        self.assertEqual(page.description, 'Some help')
        self.assertEqual(page.visible_if, '{age} > 18')
        self.assertFalse(page.is_visible)
        self.assertTrue(page.read_only)

    def test_property_defaults(self):
        creator = SurveyCreator({'pages': [{'name': 'p1', 'elements': []}]})
        page = creator.pages[0]
        self.assertEqual(page.description, '')
        self.assertEqual(page.visible_if, '')
        self.assertTrue(page.is_visible)
        self.assertFalse(page.read_only)

    def test_localized_title(self):
        creator = SurveyCreator(
            {'pages': [{'name': 'p1', 'title': {'default': 'Hello', 'fr': 'Bonjour'}, 'elements': []}]},
            language='fr',
        )
        self.assertEqual(creator.pages[0].title, 'Bonjour')

    def test_localized_title_falls_back_to_first_locale(self):
        creator = SurveyCreator(
            {'pages': [{'name': 'p1', 'title': {'default': 'Hello'}, 'elements': []}]},
            language='fr',
        )
        self.assertEqual(creator.pages[0].title, 'Hello')

    def test_i18n_title(self):
        creator = SurveyCreator(
            {'pages': [{'name': 'p1', 'title': 'Hello', 'elements': []}]},
            language='fr',
            i18n={'fr': {'Hello': 'Bonjour'}},
        )
        self.assertEqual(creator.pages[0].title, 'Bonjour')


if __name__ == '__main__':
    unittest.main()
