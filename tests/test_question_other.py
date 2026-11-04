# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for the "Other" item of choice questions, and the comment stored
next to a question's value (`<name>-Comment`)."""

import unittest

from surveyjs import SurveyCreator, SurveyForm

CHOICES = [{"value": "a", "text": "Alpha"}, {"value": "b", "text": "Beta"}]


def make_form(question, data, **survey):
    """A form of one question, `question` (its schema) answered with `data`."""
    schema = dict(survey, elements=[dict({"name": "q", "choices": CHOICES}, **question)])
    return SurveyForm(data, creator=SurveyCreator(schema)).questions["q"]


class TestOtherValue(unittest.TestCase):
    def test_dropdown_other_comment(self):
        q = make_form(
            {"type": "dropdown", "showOtherItem": True, "otherText": "Something else"},
            {"q": "other", "q-Comment": "My own"},
        )
        self.assertEqual(q.comment, "My own")
        self.assertEqual(q.other_value, "My own")
        self.assertEqual(q.value_text, "My own")

    def test_dropdown_other_without_text(self):
        q = make_form({"type": "dropdown", "showOtherItem": True, "otherText": "Something else"}, {"q": "other"})
        self.assertIsNone(q.other_value)
        self.assertEqual(q.value_text, "Something else")

    def test_dropdown_choice_picked(self):
        # A comment left from an earlier "Other" pick is no answer of it.
        q = make_form({"type": "dropdown", "showOtherItem": True}, {"q": "a", "q-Comment": "Stale"})
        self.assertIsNone(q.other_value)
        self.assertEqual(q.value_text, "Alpha")

    def test_legacy_has_other(self):
        q = make_form({"type": "radiogroup", "hasOther": True}, {"q": "other", "q-Comment": "My own"})
        self.assertTrue(q.has_other)
        self.assertEqual(q.value_text, "My own")

    def test_no_other_item(self):
        q = make_form({"type": "dropdown"}, {"q": "other", "q-Comment": "Note"})
        self.assertEqual(q.comment, "Note")
        self.assertIsNone(q.other_value)
        self.assertEqual(q.value_text, "other")

    def test_checkbox_other_comment(self):
        q = make_form({"type": "checkbox", "showOtherItem": True}, {"q": ["a", "other"], "q-Comment": "My own"})
        self.assertEqual(q.other_value, "My own")
        self.assertEqual(q.value_texts, ["Alpha", "My own"])

    def test_tagbox_other_comment(self):
        q = make_form({"type": "tagbox", "showOtherItem": True}, {"q": ["other"], "q-Comment": "My own"})
        self.assertEqual(q.value_texts, ["My own"])

    def test_not_stored_as_comment_on_question(self):
        # The text takes the place of 'other' in the value.
        q = make_form({"type": "dropdown", "showOtherItem": True, "storeOthersAsComment": False}, {"q": "My own"})
        self.assertEqual(q.other_value, "My own")
        self.assertEqual(q.value_text, "My own")

    def test_not_stored_as_comment_on_survey(self):
        q = make_form({"type": "checkbox", "showOtherItem": True}, {"q": ["b", "My own"]}, storeOthersAsComment=False)
        self.assertEqual(q.other_value, "My own")
        self.assertEqual(q.value_texts, ["Beta", "My own"])

    def test_comment_area_takes_the_key(self):
        q = make_form(
            {"type": "radiogroup", "showOtherItem": True, "showCommentArea": True},
            {"q": "My own", "q-Comment": "A remark"},
        )
        self.assertEqual(q.comment, "A remark")
        self.assertEqual(q.other_value, "My own")

    def test_creator_has_no_value(self):
        creator = SurveyCreator(
            {"elements": [{"type": "dropdown", "name": "q", "choices": CHOICES, "showOtherItem": True}]}
        )
        q = creator.questions["q"]
        self.assertIsNone(q.comment)
        self.assertIsNone(q.other_value)


if __name__ == "__main__":
    unittest.main()
