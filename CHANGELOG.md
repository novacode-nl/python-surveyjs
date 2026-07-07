# Changelog

## 0.3.0

**Breaking:** on `SurveyCreator` / `SurveyForm`, element accessors are split into root vs. flat, with consistent `all_`-prefixed flat variants and formio `component` aliases:

- `elements` — **root** (top-level) elements, keyed by name. Nested children are reached via each container's own `elements`.
- `all_elements` — **flat** map of every element (including nested), keyed by name.
- `components` / `all_components` — aliases of `elements` / `all_elements`.
- `element_ids` renamed to `all_element_ids` — flat map of every element keyed by internal id (with alias `all_component_ids`). There is no root-level id map: ids are unique across the whole tree, so an id registry is inherently global.
- The previously added `root_elements` property is removed (use `elements`).

Fixes enabled by the split:

- `SurveyForm` now builds a proper element tree: nested elements carry their container as `parent`, instead of the previous flat `parent=None` copies of every element.
- `Element.elements_on_same_line` resolves siblings from the element's parent when nested (a panel's children), so `startWithNewLine` grouping works inside panels, not only at the top level.

## 0.2.12

Add question types:

- `buttongroup`: single-select, rendered as buttons; reuses the radiogroup choice handling and exposes item-level icon/caption properties.
- `slider`: single-value or range; `to_number`/`to_range` accessors question types, with tests.

## 0.2.11

Fix `SurveyCreator._load_elements` to recurse into `paneldynamic` children via `templateElements` (the per-row template) instead of `elements`, so nested questions inside dynamic panels are correctly registered.

## 0.2.10

Update pyproject.toml.

## 0.2.9

Update README and pyproject.toml with new description, author/maintainer info, and project URLs.

## 0.2.8

Add `max_files` property to `QuestionFile`.

## 0.2.7

Set `SurveyCreator` and `SurveyForm` default language to `"default"`.\
This aligns language behavior with SurveyJS Creator defaults and improves consistency when reading localized survey content.

## 0.2.6

Fix Element `elements_on_same_line` property to return the correct sibling elements based on `start_with_new_line` property.

This also adds the first sibling on the line, which could have no JSON `startWithNewLine` property (defaulting to `start_with_new_line` True) but still be on the same line as siblings with `start_with_new_line`.

## 0.2.5

Add Element `elements_on_same_line` property, which returns sibling elements with `start_with_new_line` property (SurveyJS: `startWithNewLine`) set to False.

## 0.2.4

Fix Element `title` property to handle i18n title dicts.

The fix handles the case where title is a dict (i18n object like `{"en": "Name", "fr": "Nom"}`) by extracting the string for the current language before it's used as a key in .get().\
If the current language isn't in the dict, it falls back to the first available language, then to `self.name`.

## 0.2.3

Add Element `start_with_new_line` property, mapped from  `startWithNewLine` in SurveyJS (Element) JSON.

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
