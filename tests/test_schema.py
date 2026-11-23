# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for check_schema and SchemaError."""

import json
import unittest

from surveyjs import SchemaError, SurveyCreator, check_schema


class TestCheckSchema(unittest.TestCase):
    def test_schemas_being_designed_pass(self):
        for schema in (
            {},
            {"pages": []},
            {"elements": [{"type": "text"}]},
            {"pages": [{"elements": [{"type": "panel", "elements": [{"name": "a"}]}]}]},
            {
                "elements": [
                    {"type": "paneldynamic", "name": "jobs", "templateElements": [{"type": "text", "name": "year"}]},
                ],
            },
        ):
            with self.subTest(schema=schema):
                self.assertEqual(check_schema(schema), [])

    def test_wrong_structures(self):
        for schema, problems in (
            ([], ["schema: not an object (got list)"]),
            ({"pages": None}, ["pages: not a list (got NoneType)"]),
            ({"pages": ["x"]}, ["pages[0]: not an object (got str)"]),
            ({"pages": [{"elements": "x"}]}, ["pages[0].elements: not a list (got str)"]),
            (
                {"elements": [{"type": "paneldynamic", "templateElements": {}}]},
                ["elements[0].templateElements: not a list (got dict)"],
            ),
            ({"elements": [{"type": "text", "name": 5}]}, ["elements[0].name: not text (got int)"]),
        ):
            with self.subTest(schema=schema):
                self.assertEqual(check_schema(schema), problems)

    def test_every_problem_is_listed(self):
        schema = {"elements": [{"type": 1}, "x", {"type": "panel", "elements": "y"}]}
        self.assertEqual(
            check_schema(schema),
            [
                "elements[0].type: not text (got int)",
                "elements[1]: not an object (got str)",
                "elements[2].elements: not a list (got str)",
            ],
        )


class TestSurveyCreatorSchemaError(unittest.TestCase):
    def test_an_unreadable_structure_raises_schema_error(self):
        for schema in ([], {"pages": "x"}, {"pages": ["x"]}, {"elements": [{"type": "text", "name": 5}]}):
            with self.subTest(schema=schema), self.assertRaises(SchemaError) as raised:
                SurveyCreator(json.dumps(schema))
            self.assertEqual(raised.exception.problems, check_schema(schema))

    def test_a_schema_error_is_a_value_error(self):
        with self.assertRaises(ValueError):
            SurveyCreator("[]")

    def test_what_parsed_before_still_parses(self):
        # Not SurveyJS's structure, but read before 1.1.0 without an error.
        survey = SurveyCreator(json.dumps({"pages": [{"elements": "x"}]}))
        self.assertEqual(list(survey.elements), [])

    def test_invalid_json_is_still_a_json_error(self):
        with self.assertRaises(json.JSONDecodeError):
            SurveyCreator("{not json")
