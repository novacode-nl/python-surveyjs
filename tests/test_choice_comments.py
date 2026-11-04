# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for comments per choice and the checkbox `valuePropertyName`.

A choice with its own comment area (`choices[].showCommentArea`) stores the
comment inside the value: `{"value": "service", "comment": "Too slow"}`. A
checkbox stores every picked item as an object then, and also when it has a
`valuePropertyName` (`[{"car": "Ford"}]`). `value` is always the plain choice
values; the comments are in `choice_comments`.
"""

import unittest
from datetime import date

from surveyjs import SurveyCreator, SurveyForm

CHOICES = ["price", {"value": "service", "text": "Service", "showCommentArea": True}]


def make_question(question, raw_value):
    question = dict({"name": "q", "choices": CHOICES}, **question)
    data = {} if raw_value is None else {"q": raw_value}
    return SurveyForm(data, creator=SurveyCreator({"elements": [question]})).questions["q"]


class TestSingleChoice(unittest.TestCase):
    """radiogroup, dropdown and buttongroup: an object only when a comment
    was typed."""

    TYPES = ("radiogroup", "dropdown", "buttongroup")

    def test_value_is_plain(self):
        for question_type in self.TYPES:
            with self.subTest(question_type):
                q = make_question({"type": question_type}, {"value": "service", "comment": "Too slow"})
                self.assertEqual(q.value, "service")
                self.assertEqual(q.raw_value, {"value": "service", "comment": "Too slow"})

    def test_value_text(self):
        q = make_question({"type": "radiogroup"}, {"value": "service", "comment": "Too slow"})
        self.assertEqual(q.value_text, "Service")

    def test_choice_comments(self):
        q = make_question({"type": "dropdown"}, {"value": "service", "comment": "Too slow"})
        self.assertEqual(q.choice_comments, {"service": "Too slow"})

    def test_without_comment(self):
        q = make_question({"type": "radiogroup"}, "service")
        self.assertEqual(q.value, "service")
        self.assertEqual(q.choice_comments, {})

    def test_unanswered(self):
        q = make_question({"type": "radiogroup"}, None)
        self.assertIsNone(q.value)
        self.assertIsNone(q.value_text)
        self.assertEqual(q.choice_comments, {})

    def test_spec(self):
        q = make_question({"type": "radiogroup"}, None)
        self.assertEqual(
            q.value_spec(),
            {
                "anyOf": [
                    {"enum": ["price", "service"]},
                    {
                        "type": "object",
                        "properties": {"value": {"enum": ["service"]}, "comment": {"type": "string"}},
                        "additionalProperties": False,
                    },
                ]
            },
        )

    def test_spec_without_choice_comments(self):
        q = make_question({"type": "dropdown", "choices": ["price", "service"]}, None)
        self.assertEqual(q.value_spec(), {"enum": ["price", "service"]})

    def test_check_value_accepts_both_forms(self):
        for question_type in self.TYPES:
            with self.subTest(question_type):
                q = make_question({"type": question_type}, None)
                self.assertEqual(q.check_value("price"), [])
                self.assertEqual(q.check_value({"value": "service", "comment": "Too slow"}), [])

    def test_check_value_rejects(self):
        q = make_question({"type": "radiogroup"}, None)
        self.assertEqual(len(q.check_value("nope")), 1)
        # Only a choice with its own comment area may carry a comment.
        self.assertEqual(len(q.check_value({"value": "price", "comment": "x"})), 1)
        self.assertEqual(len(q.check_value({"value": "service", "note": "x"})), 1)
        self.assertEqual(len(q.check_value({"value": "service", "comment": 3})), 1)


class TestMultipleChoice(unittest.TestCase):
    """checkbox and tagbox: every picked item is an object."""

    TYPES = ("checkbox", "tagbox")
    RAW = [{"value": "price"}, {"value": "service", "comment": "Too slow"}]

    def test_value_is_plain(self):
        for question_type in self.TYPES:
            with self.subTest(question_type):
                q = make_question({"type": question_type}, self.RAW)
                self.assertEqual(q.value, ["price", "service"])
                self.assertEqual(q.raw_value, self.RAW)

    def test_value_texts(self):
        q = make_question({"type": "checkbox"}, self.RAW)
        self.assertEqual(q.value_texts, ["price", "Service"])

    def test_choice_comments(self):
        q = make_question({"type": "tagbox"}, self.RAW)
        self.assertEqual(q.choice_comments, {"service": "Too slow"})

    def test_empty_comment_left_out(self):
        q = make_question({"type": "checkbox"}, [{"value": "service", "comment": ""}])
        self.assertEqual(q.choice_comments, {})

    def test_spec(self):
        q = make_question({"type": "checkbox"}, None)
        self.assertEqual(
            q.value_spec(),
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"value": {"enum": ["price", "service"]}, "comment": {"type": "string"}},
                },
            },
        )

    def test_other_item_comment_does_not_count(self):
        """Only a choice other than "Other" makes the items objects."""
        q = make_question({"type": "checkbox", "choices": ["a", {"value": "other", "showCommentArea": True}]}, None)
        self.assertEqual(q.value_spec(), {"type": "array", "items": {"enum": ["a", "other"]}})


class TestValuePropertyName(unittest.TestCase):
    """A checkbox with `valuePropertyName` stores `[{"car": "Ford"}]`."""

    def make(self, raw_value, **extra):
        question = dict({"type": "checkbox", "choices": ["Ford", "Tesla"], "valuePropertyName": "car"}, **extra)
        return make_question(question, raw_value)

    def test_value_property_name(self):
        self.assertEqual(self.make(None).value_property_name, "car")

    def test_value_is_plain(self):
        q = self.make([{"car": "Ford"}, {"car": "Tesla"}])
        self.assertEqual(q.value, ["Ford", "Tesla"])
        self.assertEqual(q.value_texts, ["Ford", "Tesla"])

    def test_spec(self):
        self.assertEqual(
            self.make(None).value_spec(),
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"car": {"enum": ["Ford", "Tesla"]}},
                },
            },
        )

    def test_with_choice_comment(self):
        q = make_question({"type": "checkbox", "valuePropertyName": "car"}, [{"car": "service", "comment": "Too slow"}])
        self.assertEqual(q.value, ["service"])
        self.assertEqual(q.choice_comments, {"service": "Too slow"})

    def test_other_text(self):
        """The "Other" text is still stored next to the value."""
        schema = {
            "elements": [
                {
                    "type": "checkbox",
                    "name": "q",
                    "choices": ["Ford"],
                    "valuePropertyName": "car",
                    "showOtherItem": True,
                }
            ]
        }
        data = {"q": [{"car": "other"}], "q-Comment": "Volvo"}
        q = SurveyForm(data, creator=SurveyCreator(schema)).questions["q"]
        self.assertEqual(q.value, ["other"])
        self.assertEqual(q.other_value, "Volvo")
        self.assertEqual(q.value_texts, ["Volvo"])


class TestMatrixCells(unittest.TestCase):
    """A matrix cell reads the same however it is reached: `get_cell(...).value`,
    `get_cell_value()`, `get_row_value()` and the matrix's `value`."""

    COLUMNS = [
        {"name": "cars", "cellType": "checkbox", "choices": ["Ford", "Tesla"], "valuePropertyName": "car"},
        {"name": "reason", "cellType": "radiogroup", "choices": CHOICES},
        {"name": "start", "cellType": "text", "inputType": "date"},
    ]
    ROW = {"cars": [{"car": "Ford"}], "reason": {"value": "service", "comment": "Too slow"}, "start": "2024-03-15"}
    PARSED = {"cars": ["Ford"], "reason": "service", "start": date(2024, 3, 15)}

    def test_matrixdynamic(self):
        schema = {"elements": [{"type": "matrixdynamic", "name": "m", "columns": self.COLUMNS}]}
        q = SurveyForm({"m": [self.ROW]}, creator=SurveyCreator(schema)).questions["m"]
        self.assertEqual(q.value, [self.PARSED])
        self.assertEqual(q.get_row_value(0), self.PARSED)
        for name, parsed in self.PARSED.items():
            with self.subTest(name):
                self.assertEqual(q.get_cell_value(0, name), parsed)
                self.assertEqual(q.get_cell(0, name).value, parsed)
        self.assertEqual(q.get_cell(0, "reason").choice_comments, {"service": "Too slow"})
        self.assertEqual(q.raw_value, [self.ROW])

    def test_matrixdropdown(self):
        schema = {"elements": [{"type": "matrixdropdown", "name": "m", "rows": ["r1"], "columns": self.COLUMNS}]}
        q = SurveyForm({"m": {"r1": self.ROW}}, creator=SurveyCreator(schema)).questions["m"]
        self.assertEqual(q.value, {"r1": self.PARSED})
        self.assertEqual(q.get_row_value("r1"), self.PARSED)
        for name, parsed in self.PARSED.items():
            with self.subTest(name):
                self.assertEqual(q.get_cell_value("r1", name), parsed)
                self.assertEqual(q.get_cell("r1", name).value, parsed)

    def test_undeclared_row_parses_per_column(self):
        """A submitted row the schema does not declare has no cell questions."""
        schema = {"elements": [{"type": "matrixdropdown", "name": "m", "rows": ["r1"], "columns": self.COLUMNS}]}
        q = SurveyForm({"m": {"r9": {"start": "2024-03-15"}}}, creator=SurveyCreator(schema)).questions["m"]
        self.assertEqual(q.value, {"r9": {"start": date(2024, 3, 15)}})


if __name__ == "__main__":
    unittest.main()
