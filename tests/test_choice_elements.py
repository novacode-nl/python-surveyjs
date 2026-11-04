# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for questions inside a choice (`choices[].elements`).

A checkbox or radiogroup choice can hold questions of its own, shown when it
is picked. SurveyJS stores their answers next to the question's own:
`{"contact": "phone", "phone_number": "0612345678"}`.
"""

import unittest
from datetime import time

from surveyjs import SurveyCreator, SurveyForm

PHONE = {
    "value": "phone",
    "elements": [
        {"type": "text", "name": "phone_number", "isRequired": True},
        {"type": "text", "name": "call_after", "inputType": "time"},
    ],
}


def schema(question_type="radiogroup"):
    return {"elements": [{"type": question_type, "name": "contact", "choices": ["email", PHONE]}]}


def make_form(data, question_type="radiogroup"):
    return SurveyForm(data, creator=SurveyCreator(schema(question_type)))


class TestChoiceElements(unittest.TestCase):
    def setUp(self):
        self.form = make_form({"contact": "phone", "phone_number": "0612345678", "call_after": "18:00"})

    def test_are_questions(self):
        self.assertEqual(list(self.form.questions), ["contact", "phone_number", "call_after"])

    def test_value_is_parsed(self):
        self.assertEqual(self.form.questions["call_after"].value, time(18, 0))

    def test_path(self):
        self.assertEqual(self.form.questions["call_after"].path_str, "contact.call_after")
        self.assertIs(self.form.get_element_by_path("contact.call_after"), self.form.questions["call_after"])

    def test_input_path_is_next_to_the_question(self):
        self.assertEqual(self.form.questions["call_after"].input_path, ["call_after"])

    def test_parent_and_choice_value(self):
        call_after = self.form.questions["call_after"]
        self.assertIs(call_after.parent, self.form.questions["contact"])
        self.assertEqual(call_after.choice_value, "phone")

    def test_choice_question_value_unchanged(self):
        self.assertEqual(self.form.questions["contact"].value, "phone")

    def test_on_a_creator(self):
        creator = SurveyCreator(schema())
        self.assertEqual(list(creator.questions), ["contact", "phone_number", "call_after"])
        self.assertEqual(creator.all_elements["call_after"].choice_value, "phone")

    def test_checkbox(self):
        form = make_form({"contact": ["email", "phone"], "call_after": "18:00"}, "checkbox")
        self.assertEqual(form.questions["call_after"].value, time(18, 0))

    def test_not_supported_types(self):
        """In SurveyJS only checkbox and radiogroup have questions in a choice."""
        for question_type in ("dropdown", "tagbox", "buttongroup"):
            with self.subTest(question_type):
                form = make_form({"contact": "phone"}, question_type)
                self.assertEqual(list(form.questions), ["contact"])


class TestChoiceElementsValidation(unittest.TestCase):
    """SurveyJS hides and skips the questions of a choice that is not picked."""

    def test_required_when_picked(self):
        form = make_form({"contact": "phone"})
        self.assertEqual(form.validation_errors(), {"phone_number": {"required": "phone_number is required"}})

    def test_skipped_when_not_picked(self):
        form = make_form({"contact": "email"})
        self.assertTrue(form.questions["phone_number"].in_unpicked_choice)
        self.assertEqual(form.validation_errors(), {})

    def test_skipped_when_unanswered(self):
        self.assertEqual(make_form({}).validation_errors(), {})

    def test_checkbox_picked(self):
        form = make_form({"contact": ["email", "phone"]}, "checkbox")
        self.assertFalse(form.questions["phone_number"].in_unpicked_choice)
        self.assertIn("phone_number", form.validation_errors())

    def test_answer_of_unpicked_choice_still_read(self):
        """Read what is in the data, even when its choice is not picked."""
        form = make_form({"contact": "email", "phone_number": "0612345678"})
        self.assertEqual(form.questions["phone_number"].value, "0612345678")


class TestChoiceElementsInDynamicPanel(unittest.TestCase):
    def setUp(self):
        survey = {"elements": [{"type": "paneldynamic", "name": "people", "templateElements": schema()["elements"]}]}
        data = {"people": [{"contact": "phone", "call_after": "18:00"}]}
        self.people = SurveyForm(data, creator=SurveyCreator(survey)).questions["people"]

    def test_row_child(self):
        call_after = self.people.get_panel(0)["contact"].elements["call_after"]
        self.assertEqual(call_after.value, time(18, 0))
        self.assertEqual(call_after.input_path, ["people", 0, "call_after"])

    def test_panel_value_parses_it(self):
        self.assertEqual(self.people.value, [{"contact": "phone", "call_after": time(18, 0)}])


class TestChoiceElementsValueSpec(unittest.TestCase):
    def test_spec_next_to_the_question(self):
        properties = SurveyCreator(schema()).value_spec()["properties"]
        self.assertEqual(list(properties), ["contact", "phone_number", "call_after"])
        self.assertEqual(properties["call_after"]["format"], "time")


if __name__ == "__main__":
    unittest.main()
