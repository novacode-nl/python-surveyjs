# Changelog

## 0.2.3

Add `start_with_new_line` property to Element class, mapped from  `startWithNewLine` in SurveyJS (Element) JSON.

## 0.2.2

Update README.

## 0.2.1

Update README.

## 0.2.0

Align to SurveyJS terminology and structure:
- Rename `questions` package to `elements`; base class `Question` → `Element`.
- Add `Question` and `Layout` subclasses of `Element` (new `question.py`, `layout.py`).
- Rename `SurveyCreator` internals: `question_class_mapping` → `element_class_mapping`, `load_questions()` → `load_elements()`, `get_question_class()` → `get_element_class()`, `get_question_object()` → `get_element_object()`.
- `SurveyCreator.elements` now holds all elements; `questions` is reserved for input-only fields.
- Update `Panel` to use `Layout` as base class; `Html` and `Image` updated accordingly.
- Update `SurveyForm` and all tests for the new naming.

## 0.1.1

Add `custom_properties` getter to the Question class, stored as `customProperties` property in a SurveyJS Question JSON.

This is useful for accessing any additional metadata or configuration that may be included in the survey schema but is not part of the standard question properties.

More info:
https://surveyjs.io/form-library/documentation/customize-question-types/add-custom-properties-to-a-form

## 0.1.0

Initial release.
