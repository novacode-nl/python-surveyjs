# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for `valueName` ("Join identifier" in SurveyJS Creator).

A question with a `valueName` stores its value under that key instead of its
`name`. The `name` stays the identifier for lookups and paths.
"""

import unittest
from datetime import date

from surveyjs import SurveyCreator, SurveyForm

SCHEMA = {
    "elements": [
        {"type": "text", "name": "q1", "valueName": "email"},
        {"type": "text", "name": "q2", "valueName": "email"},
        {"type": "radiogroup", "name": "q3", "valueName": "color", "choices": ["red", "blue"], "showOtherItem": True},
        {"type": "text", "name": "plain"},
        {
            "type": "paneldynamic",
            "name": "q4",
            "valueName": "jobs",
            "templateElements": [
                {"type": "text", "name": "q5", "valueName": "employer"},
                {"type": "text", "name": "start", "inputType": "date"},
            ],
        },
    ]
}

DATA = {
    "email": "a@b.c",
    "color": "other",
    "color-Comment": "Turquoise",
    "plain": "hi",
    "jobs": [{"employer": "Nova Code", "start": "2020-01-06"}],
}


def make_form(data=DATA):
    return SurveyForm(data, creator=SurveyCreator(SCHEMA))


class TestValueName(unittest.TestCase):
    def setUp(self):
        self.q = make_form().questions

    def test_value_name(self):
        self.assertEqual(self.q["q1"].value_name, "email")

    def test_value_name_defaults_to_name(self):
        self.assertEqual(self.q["plain"].value_name, "plain")

    def test_value_read_from_value_name(self):
        self.assertEqual(self.q["q1"].value, "a@b.c")

    def test_input_path(self):
        self.assertEqual(self.q["q1"].input_path, ["email"])

    def test_name_stays_the_identifier(self):
        """Looked up and addressed by name, not by valueName."""
        form = make_form()
        self.assertNotIn("email", form.questions)
        self.assertEqual(form.get_value("q1"), "a@b.c")
        self.assertEqual(form.get_element_by_path("q1").path, ["q1"])

    def test_questions_sharing_a_value_name_share_the_value(self):
        self.assertEqual(self.q["q2"].value, "a@b.c")

    def test_comment_under_value_name(self):
        self.assertEqual(self.q["q3"].comment_name, "color-Comment")
        self.assertEqual(self.q["q3"].comment, "Turquoise")
        self.assertEqual(self.q["q3"].value_text, "Turquoise")


class TestValueNameInDynamicPanel(unittest.TestCase):
    """A dynamic panel's rows are stored under its valueName, and a row's
    question under its own."""

    def setUp(self):
        self.q4 = make_form().questions["q4"]

    def test_rows_read_from_value_name(self):
        self.assertEqual(len(self.q4.panels), 1)

    def test_row_child_value(self):
        self.assertEqual(self.q4.get_panel(0)["q5"].value, "Nova Code")

    def test_row_child_input_path(self):
        self.assertEqual(self.q4.get_panel(0)["q5"].input_path, ["jobs", 0, "employer"])

    def test_row_child_path_uses_names(self):
        self.assertEqual(self.q4.get_panel(0)["q5"].path_str, "q4[0].q5")

    def test_panel_value_parses_by_value_name(self):
        self.assertEqual(self.q4.value, [{"employer": "Nova Code", "start": date(2020, 1, 6)}])


class TestValueNameInValueSpec(unittest.TestCase):
    def test_spec_keyed_by_value_name(self):
        spec = SurveyCreator(SCHEMA).value_spec()
        properties = spec["properties"]
        self.assertIn("email", properties)
        self.assertIn("jobs", properties)
        self.assertNotIn("q1", properties)
        self.assertIn("employer", properties["jobs"]["items"]["properties"])


if __name__ == "__main__":
    unittest.main()
