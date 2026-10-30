# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Changed

- `SurveyForm()` raises `ValueError` instead of a plain `Exception` when given both `creator` and `creator_schema_json`, or neither. Code that catches `Exception` still works.

## 0.9.1

No changes to the package itself.

### Security

- Releases are now built and published from GitHub Actions with PyPI Trusted Publishing, so each file on PyPI comes with a provenance attestation linking it to the commit and workflow that built it.

## 0.9.0

What a question accepts as its value, for code that writes data into a form.

### Added

- `value_spec()` on every element: the value it accepts, as a small subset of JSON Schema (`type`, `enum`, `format`, `items`, `properties`, ...), or None for an element that holds no value (panel, html, image, expression).
- `SurveyCreator.value_spec()`: the spec of the survey's data: an object keyed by the questions at its top level (those in a plain panel included), each with its own spec, nested for dynamic panels, matrices and multiple text.
- `check_value(value)` on every element, and `SurveyCreator.check_values(values)` for a dict of values keyed by question name: both return a list of problems, empty when everything fits. Each problem starts with the data path of the value, e.g. `jobs[1].year: expected a number, got str`.

  ```python
  creator.check_values({'birthDate': date(1985, 6, 14)})
  # ["birthDate: expected a string in the format YYYY-MM-DD (e.g. '2024-03-15'), got date"]
  ```

- The problems name what was expected and the type that was given, never the value itself, so they can be logged or passed on without disclosing any data.

- `surveyjs.valuespec`: `check_spec()`, `input_type_spec()` and `data_properties()`.

## 0.8.0

A name is unique per data level only: two dynamic panels can each hold a `year`. Looking up such a name now raises instead of returning one of them.

### Breaking Changes

**Looking up an ambiguous name raises `AmbiguousNameError`.**

- `questions`, `all_elements` and `elements` (on `SurveyCreator` and `SurveyForm`) used to return the last element with that name.\
- `[name]` and `.get(name)` now raise, and so do `get_value()`, `get_raw_value()`, `get_question_by_name()` and `form.data.<name>`.
- `in` and iterating are unchanged.
- Use `get_element_by_path('jobs.year')`, or `get_elements_by_name('year')`.
- `AmbiguousNameError` is a `LookupError`, not a `KeyError`, so `except KeyError` does not catch it.

### Added

- `AmbiguousNameError`, with `name` and `paths`.
- `ambiguous_names` on `SurveyCreator` and `SurveyForm`: `{name: [path, ...]}`, e.g. `{'year': ['jobs.year', 'school.year']}`.
- `get_elements_by_name(name)` on `SurveyCreator` and `SurveyForm`: every element with that name, in schema order, as a list. On a form this includes each row and matrix cell.

  ```python
  [e.path_str for e in form.get_elements_by_name('year')]
  # ['jobs[0].year', 'jobs[1].year', 'school[0].year']
  ```

## 0.7.0

Overview:

- `value` now returns a Python object for booleans (`True`/`False`) and for multipletext, matrix and dynamic panel questions (with their contents parsed).
- All display texts are translated, not only titles.
- A form's `lang` applies to all its elements, including nested ones.
- Fix: `template_panel` was missing the children of nested panels.

### Breaking Changes

- **Boolean `value` is a bool.** With `valueTrue`/`valueFalse` set (e.g. `'agreed'`/`'declined'`), `value` used to return those strings. It now returns `True`, `False` or `None`.
  Change `q.value == 'agreed'` to `q.value is True`, or use `q.raw_value`.
- **`QuestionBoolean.to_bool()` returns `None` for an unrecognised value.** It used to fall back to `bool(raw_value)`, so `'maybe'` gave `True`.
- **Container `value` is parsed.** For `multipletext`, `matrixdynamic`, `matrixdropdown` and `paneldynamic`, `value` used to return `raw_value`. It now returns a parsed copy (see below), so a date item or cell is a `date` instead of a string.
  Use `q.raw_value` to get the submitted data.

### Added

- `parse_boolean(value, value_true=True, value_false=False)` in `surveyjs.elements.inputtype`. Accepts a bool, the given true/false values, and `'true'`/`'yes'`/`'on'`/`'1'` or `'false'`/`'no'`/`'off'`/`'0'` (any case). Raises `ValueError` for anything else. Also used for `inputType: "boolean"`.
- `QuestionBoolean.value_text`: `label_true` or `label_false` for the answer, `None` if unanswered. Works for boolean matrix cells too: `q.get_cell(row, column).value_text`.
- Boolean matrix columns: `get_cell_value()` and `get_row_value()` return bools, using the column's `valueTrue`/`valueFalse`.
- Container `value` is a parsed copy of `raw_value`, with the same keys and rows. `raw_value` is unchanged:

  ```python
  q.raw_value   # [{'due': '2024-04-01', 'done': 'yes'}]
  q.value       # [{'due': date(2024, 4, 1), 'done': True}]
  ```

  - `multipletext`: each item is parsed by its `inputType`, like `item_values`. Unanswered items are left out instead of `None`.
  - `matrixdynamic`, `matrixdropdown`: each cell is parsed by its column, like `get_row_value()`.
  - `paneldynamic`: each answer is parsed by its question in that panel, including questions in nested panels and containers. `PanelInstance.value` gives one row. On a SurveyCreator, `value` equals `raw_value`.
- `translate_text(text, language, i18n)` in `surveyjs.text`, and `translate(text)` on elements and pages. It handles SurveyJS localizable strings (`{"default": "Yes", "fr": "Oui"}`) and then the `i18n` map.
- `SurveyCreator.get_element_object(element, language=None)` takes the language to build the element in.

### Changed

- All display texts are translated. Before, only titles and the default error messages were. Now also:
  - descriptions (elements and pages), placeholders, `requiredErrorText` and a validator's own `text`
  - choice texts in `choices_values` (dropdown, radiogroup, checkbox, tagbox, ranking, buttongroup), and so `value_text`/`value_texts`
  - matrix `row_values`/`column_values`, multipletext item titles and matrix column titles
  - boolean `label_true`/`label_false`
  - `other_text`, rating min/max descriptions, add/remove button texts, `template_title`, image `alt_text` and html content
- A localizable string falls back to its `default` locale first, then to the first locale. Before, it went straight to the first locale.
- `SurveyForm` uses the creator's `language` when no `lang` is given. Before, it used `"default"` for the page titles.
- An explicit `SurveyForm(lang=...)` applies to all the form's elements, including panel children, dynamic panel rows and matrix cells. Before, only the page titles used it. The creator keeps its own language.
- `lang` is passed on to the creator built from `creator_schema_json`.

### Fixed

- `template_panel` (the blank row for rendering an empty form) was missing the children of a nested panel, and a nested matrixdropdown had no cells.
- `template_panel.data` returned the data of row 0 on a form with rows, and raised `IndexError` on an empty form (as did its `value`). It is now `{}`.

## 0.6.0

Matrix cells are questions.

### Added

- On a form, `matrixdynamic` and `matrixdropdown` build one question per cell. The cell's class comes from the column's `cellType`, through the survey's element class mapping. So a dropdown cell can resolve its choice text, and a custom question class is also used inside a matrix.
- `question.get_cell(row_key, column_name)`: one cell, as a question.
- `question.cells(row_key)`: a row's cells, keyed by column name.
- `question.rows_cells`: every row's cells, keyed by row key.
- `MatrixColumn.cell_raw`: the column as the element definition its cells are built from (`cellType` as `type`, its own choices or the question's).
- `Element.row_key`: the row an element belongs to in a repeating container. An int for a dynamic panel or dynamic matrix, the row name for a matrixdropdown. `panel_index` is the same value and keeps working.
- `QuestionMatrixdropdown.row_names`: the declared rows, in schema order.
- Cells are registered by path only, never by name, because a column name repeats in every row:

  ```python
  form.get_element_by_path('employeeList[1].role').value_text   # 'designer'
  form.get_element_by_path('budgetMatrix[marketing].status')
  ```

  A cell's `input_path` points to its value in the submission, e.g. `['employeeList', 2, 'salary']` or `['budgetMatrix', 'development', 'q1']`.

### Changed

- A form now creates one element per cell of a submitted matrix, like a dynamic panel already did per row. A Creator creates no cells, as it has no submission.
- `rows_data`, `get_row_value()`, `get_cell_value()`, `columns` and `parse()` are unchanged.

## 0.5.0

Form and question validation.

### Added

- `SurveyForm.validation_errors()`: errors of every input question, keyed by question name, e.g. `{'age': {'numeric': "The 'Age' should be at least 18"}}`. Questions without errors are left out, so a valid submission gives `{}`.
- `Element.validation_errors()`: one question's errors, keyed by error type. It checks the `isRequired` flag (key `required`, only when the answer is empty) and each entry of the `validators` array (only when the answer is not empty, like SurveyJS).
- `Element.is_empty()`: `None`, `''`, `[]` and `{}` are empty; `False` and `0` are answers.
- `Element.required_error_text`: the question's `requiredErrorText`, used as the required message when set.
- Validators, with SurveyJS's behaviour and default English messages:
  - `numeric`: number check, with `minValue`/`maxValue`.
  - `text`: `minLength`/`maxLength`, and `allowDigits`.
  - `answercount`: `minCount`/`maxCount` on multi-select answers.
  - `regex`: `regex` (with `caseInsensitive`), checked against each item of an array answer. A pattern that doesn't compile is ignored.
  - `email`: SurveyJS's e-mail pattern.
- A validator's own `text` overrides its message. Otherwise the default message is translated through the i18n map, and `{0}`/`{1}`/`{2}` are filled in.
- `surveyjs.elements.validators.register_validator(type_name)`: decorator to add or override a validator type, like `register_input_type`.
- The `expression` validator is not supported, as it needs a SurveyJS expression engine. Unknown validator types are skipped.

## 0.4.3

### Changed

- `QuestionText`, `MultipleTextItem` and `MatrixColumn` show `input_type` in their `repr()`.
- `MatrixColumn`'s `repr()` always shows `cell_type`, and `input_type` only when set: `<MatrixColumn name=when cell_type=text input_type=date>`, `<MatrixColumn name=role cell_type=dropdown>`. Before, the two fields were swapped.
- An `element_class_mapping` string may be a dotted path to your own class, e.g. `{'text': 'myapp.widgets.MyText'}`, not only a class name in `surveyjs.elements.<type>`.
- README: the Questions and values example shows `date` and `datetime-local` questions parsed to `datetime.date` / `datetime.datetime`, and the reprs include `input_type`.

### Fixed

- `element_class_mapping` string values never worked: the name was capitalized (`QuestionText` became `Questiontext`) and the import path was wrong. Every string mapping fell back to `Element` with a warning. Class objects as values were not affected.
- A broken import inside your own mapped module now gives the same warning, as `ImportError` is caught instead of only `ModuleNotFoundError`.

### Removed

- `surveyjs.elements.nonvalue` (`QuestionNonValue`). It could never be loaded (the loader looked for `QuestionNonvalue`), nothing used it, and SurveyJS has no `nonvalue` question type.

## 0.4.2

### Changed

- README: document `pages` on both `SurveyCreator` and `SurveyForm`. The examples now read values from `form.pages`; a creator's pages hold the schema and have no values.
- Tests check that `get_page_by_name()` works on both classes, and that their pages hold different element objects.

## 0.4.1

### Changed

- README: show that `Page.elements` is an OrderedDict of Element objects keyed by name, like `SurveyCreator.elements` / `SurveyForm.elements`. The example only showed `list(...)`, which gives the names. Also note that `page.questions` is the same, filtered to input questions.
- The README test also checks that the values are Element objects.

## 0.4.0

Pages, paths, panel instances and `inputType` parsing.

### Breaking Changes

- `SurveyCreator.pages` returns `Page` objects instead of dicts. Use `page.name` instead of `page['name']`; the dict is in `page.raw`.
- `QuestionMultipletext.items` returns `MultipleTextItem` objects instead of dicts. Use `item.name` instead of `item['name']`; the dict is in `item.raw`.
- `columns` of `matrixdropdown` and `matrixdynamic` returns `MatrixColumn` objects instead of dicts. Use `column.name` instead of `column['name']`; the dict is in `column.raw`.
- `Element.value` is `raw_value` parsed by the element's `inputType`, and is read-only. Set `raw_value` instead. Only date/time/number questions return something different. An unparseable value gives `None`, with the original in `raw_value`. `to_dict()` writes `raw_value` under its `value` key.
- `get_item_value()` (multipletext) and `get_cell_value()` / `get_row_value()` (matrices) are parsed by the item's or column's `inputType`. Use `get_item_raw_value()`, `get_cell_raw_value()` and `get_row_raw_value()` for the submitted values.
- Element ids are removed: `Element.id`, `all_element_ids` and `all_component_ids`. The ids were random uuids, different on each parse and between a creator and its form. Use `path` / `all_element_paths` instead. An `id` in the schema is still in `element.raw['id']`.
- `QuestionPaneldynamic.get_panel_value(index, field)` reads through the element: it returns the field's `defaultValue` when a row leaves it out (was `None`), and a negative `index` returns `None` (was the last row).

### Added

- Pages:
  - `SurveyCreator.pages` / `SurveyForm.pages`: `Page` objects in schema order, with `name`, `title` (translated), `description`, `visible_if`, `is_visible`, `read_only`, `index`, `elements`, `questions` and `raw`.
  - `get_page_by_name()` on both classes, and `Element.page`. Nested elements get the page of their container.
  - A schema without pages (top-level `elements`) gets one page named `page1`.
  - Pages are not elements; they are not in `elements`, `all_elements`, `questions` or `all_element_paths`.
- Paths:
  - `Element.path` / `path_str`: the position in the survey, e.g. `contactPanel.phone`. Unique, the same on each parse and between a creator element and its form element.
  - `Element.input_path` / `input_path_str`: where the value is in the submission, e.g. `['education', 0, 'year']`. A `panel` adds no level, a `paneldynamic` does. `Element.get_value_from(data)` reads it.
  - `all_element_paths` (alias `all_component_paths`) and `get_element_by_path()` on both classes.
  - `Element.nests_data`, `panel_index`, `in_repeating_context` and `registrable_children`.
  - The unused `survey_path` / `survey_input_path` attributes are renamed to `path` / `input_path` and now computed.
- Panel instances:
  - A form builds one set of child elements per row of a dynamic panel, with values: `paneldynamic.panels` (a list of `PanelInstance`) and `get_panel(index)`. A creator only has the template children, in `elements`.
  - Row children are registered by path only (`education[0].year`), not in `all_elements` or `questions`, because each row reuses the same names.
  - `Element.load()` has `register_with_owner` / `register_with_parent` flags for this.
  - `Element.panel_instance`: the `PanelInstance` an element belongs to, or `None`.
  - `QuestionPaneldynamic.template_panel`: a blank row built from the template, for rendering an empty form. Built once, from new element objects, so the creator's template children are not changed.
- Text piping:
  - `surveyjs.text.interpolate_text(text, panel_index=None)`, also as `surveyjs.interpolate_text`.
  - `Element.title`, `label` and `description` replace `{panelIndex}` with the 1-based row number, like SurveyJS. Elements deeper in a row use their container's row. Outside a dynamic panel the placeholder is left as is. Other placeholders are not supported.
  - `PanelInstance.title`: the paneldynamic's `templateTitle` for that row.
- `inputType` parsing:
  - `surveyjs.elements.inputtype`: one set of parsers per `inputType`, used by text questions, multipletext items and matrix columns. `date` gives a `date`, `datetime-local` a `datetime`, `time` a `time`, `month` a `date` (first of the month), `week` a `date` (Monday of the ISO week), `number` / `range` an `int` / `float`. Other types are returned unchanged; `None` or an unparseable value gives `None`.
  - `surveyjs.register_input_type(input_type, parser)` adds or replaces a parser; `surveyjs.parse_input_value(input_type, value)` applies one.
  - `QuestionText.to_time()`, `to_month()` and `to_week()`, next to `to_number()`, `to_date()` and `to_datetime()`. They parse `raw_value` as that type, whatever the `inputType`.
  - Multipletext items each have their own `inputType`: `question.item_values`, `question.raw_item_values`, `question.get_item(name)`, and `raw_value` / `value` on an item. `MultipleTextItem` has `name`, `title`, `input_type`, `is_required` and `placeholder`.
  - Matrix columns with `cellType: "text"` can have an `inputType` too. `MatrixColumn` has `name`, `title`, `cell_type` and `choices` (both default to the question's), `input_type`, `is_required` and `parse(value)`. The matrix questions have `column_names`, `column_count`, `get_column(name)`, `get_row_value(row)`, `get_row_raw_value(row)` and `get_cell_raw_value(row, column)`.
  - `SurveyForm.get_raw_value(name)`, next to `get_value(name)`.
  - `matrix` (single-select) is not affected. `rows_data`, `panels_data` and `column_values` still return the submitted data.

### Fixed

- `Element.elements_on_same_line` raised `ValueError` for a child of a dynamic panel row. It now uses the row's elements.
- `QuestionText.to_date()` returned a `datetime` unchanged instead of a `date`.
- `SurveyCreator` built every panel child twice.
- Two dynamic panels can have template children with the same name (e.g. `year`). In `all_elements` the last one wins; `all_element_paths` has both (`jobs.year`, `school.year`).
- Removed unused imports.

## 0.3.0

### Breaking Changes

- Element accessors on `SurveyCreator` / `SurveyForm` are split into root and flat:
  - `elements`: only the root (top-level) elements, keyed by name. Nested elements are in their container's `elements`.
  - `all_elements`: every element, including nested ones, keyed by name.
  - `components` / `all_components`: aliases of `elements` / `all_elements`.
  - `element_ids` is renamed to `all_element_ids` (alias `all_component_ids`), keyed by internal id. (Removed in 0.4.0.)
  - `root_elements` is removed; use `elements`.

### Fixed

- `SurveyForm` builds a real element tree: nested elements have their container as `parent`. Before, every element was a flat copy with `parent=None`.
- `Element.elements_on_same_line` also works inside panels, using the element's parent.

## 0.2.12

### Added

- `buttongroup` question type: single-select shown as buttons, with the radiogroup choice handling and item icon/caption properties.
- `slider` question type: a single value or a range, with `to_number()` / `to_range()`.

## 0.2.11

### Fixed

- `SurveyCreator._load_elements` now reads the children of a `paneldynamic` from `templateElements` instead of `elements`, so questions in dynamic panels are registered.

## 0.2.10

### Changed

- Update pyproject.toml.

## 0.2.9

### Changed

- Update the README and pyproject.toml: description, author/maintainer and project URLs.

## 0.2.8

### Added

- `QuestionFile.max_files`.

## 0.2.7

### Changed

- `SurveyCreator` and `SurveyForm` use `"default"` as default language, like SurveyJS Creator.

## 0.2.6

### Fixed

- `Element.elements_on_same_line` returns the right siblings, based on `start_with_new_line`. It now also includes the first element on the line, which may have no `startWithNewLine` in the JSON.

## 0.2.5

### Added

- `Element.elements_on_same_line`: sibling elements with `start_with_new_line` (SurveyJS: `startWithNewLine`) set to False.

## 0.2.4

### Fixed

- `Element.title` handles a translated title dict like `{"en": "Name", "fr": "Nom"}`. It uses the current language, then the first language, then the element name.

## 0.2.3

### Added

- `Element.start_with_new_line`, from `startWithNewLine` in the SurveyJS JSON.

## 0.2.2

### Changed

- Update README.

## 0.2.1

### Changed

- Update README.

## 0.2.0

Align with SurveyJS terminology and structure.

### Breaking Changes

- The `questions` package is renamed to `elements`, and the base class `Question` to `Element`.
- `SurveyCreator` renames: `question_class_mapping` to `element_class_mapping`, `load_questions()` to `load_elements()`, `get_question_class()` to `get_element_class()` and `get_question_object()` to `get_element_object()`.
- `SurveyCreator.elements` holds all elements; `questions` only holds input questions.

### Added

- `Question` and `Layout` subclasses of `Element` (`question.py`, `layout.py`).

### Changed

- `Panel`, `Html` and `Image` use `Layout` as base class.
- `SurveyForm` and the tests use the new names.

## 0.1.1

### Added

- `custom_properties` on questions: the `customProperties` of a SurveyJS question, for extra metadata in the schema. See <https://surveyjs.io/form-library/documentation/customize-question-types/add-custom-properties-to-a-form>.

## 0.1.0

Initial release.
