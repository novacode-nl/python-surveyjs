# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for `SurveyCreator.get_element_class` and `element_class_mapping`.

A mapping value may be a class object, a bare class name (looked up in this
library's `surveyjs.elements.<type>` module), or a dotted path to a class of
your own. Anything unresolvable falls back to the base `Element`.
"""

import sys
import types
import unittest

from surveyjs import SurveyCreator
from surveyjs.elements.element import Element
from surveyjs.elements.text import QuestionText

SCHEMA = {'elements': [{'type': 'text', 'name': 'x'}]}


class MyText(QuestionText):
    """A custom class living outside `surveyjs.elements`."""


def element_class(mapping=None):
    creator = SurveyCreator(
        SCHEMA,
        element_class_mapping={'text': mapping} if mapping is not None else {},
    )
    return type(creator.all_elements['x'])


class TestElementClassMapping(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # A module a dotted path can resolve against.
        module = types.ModuleType('surveyjs_test_widgets')
        module.MyText = MyText
        sys.modules['surveyjs_test_widgets'] = module

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop('surveyjs_test_widgets', None)

    def test_no_mapping_derives_the_class_from_the_type(self):
        self.assertIs(element_class(), QuestionText)

    def test_class_object(self):
        self.assertIs(element_class(MyText), MyText)

    def test_bare_class_name_is_used_verbatim(self):
        """Regression: the name was `.capitalize()`d into 'Questiontext',
        and the import path appended it as if it were a module, so no string
        mapping ever resolved."""
        self.assertIs(element_class('QuestionText'), QuestionText)

    def test_bare_class_name_is_not_capitalised(self):
        """'QuestionText'.capitalize() == 'Questiontext' -- a class that does
        not exist. A CamelCase name must survive intact."""
        self.assertIs(element_class('QuestionText'), QuestionText)
        self.assertIsNot(element_class('QuestionText'), Element)

    def test_lowercase_name_is_not_silently_fixed_up(self):
        """The name is a class name, not a type name: no case coercion."""
        with self.assertLogs('surveyjs.creator', level='WARNING'):
            self.assertIs(element_class('questiontext'), Element)

    def test_dotted_path_to_a_custom_class(self):
        self.assertIs(element_class('surveyjs_test_widgets.MyText'), MyText)

    def test_dotted_path_into_the_library(self):
        self.assertIs(element_class('surveyjs.elements.text.QuestionText'), QuestionText)

    def test_unknown_class_name_falls_back_to_element(self):
        with self.assertLogs('surveyjs.creator', level='WARNING') as cm:
            self.assertIs(element_class('DoesNotExist'), Element)
        self.assertIn("Could not load element class for type 'text'", cm.output[0])

    def test_unknown_module_falls_back_to_element(self):
        with self.assertLogs('surveyjs.creator', level='WARNING'):
            self.assertIs(element_class('no.such.module.Thing'), Element)

    def test_unknown_type_falls_back_to_element(self):
        creator = SurveyCreator({'elements': []})
        with self.assertLogs('surveyjs.creator', level='WARNING') as cm:
            cls = creator.get_element_class({'type': 'unknowntype'})
        self.assertIs(cls, Element)
        self.assertIn("Could not load question class for type 'unknowntype'", cm.output[0])

    def test_element_without_a_type(self):
        creator = SurveyCreator({'elements': []})
        self.assertIsNone(creator.get_element_class({'name': 'x'}))

    def test_mapped_class_is_actually_instantiated(self):
        creator = SurveyCreator(SCHEMA, element_class_mapping={'text': 'surveyjs_test_widgets.MyText'})
        element = creator.all_elements['x']
        self.assertIsInstance(element, MyText)
        self.assertEqual(element.name, 'x')
        self.assertEqual(element.input_type, 'text')


class TestNonValueModuleIsGone(unittest.TestCase):
    """`surveyjs.elements.nonvalue` was an unreachable copy of the pre-0.4.0
    `text.py`: never loadable by type name (the loader derives
    'QuestionNonvalue', the class was 'QuestionNonValue'), unreferenced, and
    frozen with the `to_date()` bug 0.4.0 fixed."""

    def test_module_is_removed(self):
        with self.assertRaises(ImportError):
            import surveyjs.elements.nonvalue  # noqa: F401

    def test_nonvalue_type_falls_back_to_element(self):
        creator = SurveyCreator({'elements': []})
        with self.assertLogs('surveyjs.creator', level='WARNING'):
            self.assertIs(creator.get_element_class({'type': 'nonvalue'}), Element)


if __name__ == '__main__':
    unittest.main()
