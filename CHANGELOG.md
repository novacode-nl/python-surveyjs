# Changelog

## 0.4.0

Adds first-class **pages**, **paths**, **panel instances**, and **`inputType` parsing**.

**Breaking:**

- `SurveyCreator.pages` returns `Page` objects instead of raw schema dicts. Use `page.name` in place of `page['name']`; the raw dict remains available as `page.raw`.
- `QuestionMultipletext.items` returns `MultipleTextItem` objects instead of raw item dicts. Use `item.name` in place of `item['name']`; the raw dict remains available as `item.raw`.
- `QuestionMatrixdropdown.columns` and `QuestionMatrixdynamic.columns` return `MatrixColumn` objects instead of raw column dicts. Use `column.name` in place of `column['name']`; the raw dict remains available as `column.raw`.
- **`Element.value` is now `raw_value` parsed per the element's `inputType`, and is read-only.** `raw_value` holds the value exactly as submitted and is the settable one. For every element without an `inputType` — all types but `text` and `multipletext` items — the two are equal, so only date/time/number questions change. `to_dict()` emits `raw_value` under its `value` key, since a parsed `date` is not JSON-serialisable. A value that cannot be parsed yields `value is None` while `raw_value` keeps the original, which is what distinguishes a malformed submission from an empty one.
- `QuestionMultipletext.get_item_value(name)` and the matrix questions' `get_cell_value(...)` / `get_row_value(...)` now parse per the item's or column's own `inputType`. Their unparsed counterparts are `get_item_raw_value(name)`, `get_cell_raw_value(...)` and `get_row_raw_value(...)`.
- **Element ids are removed entirely**: `Element.id`, `all_element_ids` and its `all_component_ids` alias are gone. SurveyJS identifies elements by `name` and does not serialise an `id` onto them, so `Element.id` was always a freshly generated uuid — unstable across parses, and different between a `SurveyCreator` element and its `SurveyForm` counterpart, which made the registry useless for correlating the two. This retracts the 0.3.0 note below claiming ids are "unique across the whole tree": they were unique only because they were random. Use `path` / `all_element_paths` for a stable, unique handle on an element. An `id` in the schema JSON is now ignored (it remains readable via `element.raw['id']`).
- `QuestionPaneldynamic.get_panel_value(index, field)` now reads through the element rather than the raw submission dict. It therefore honours the field's `defaultValue` where a row omits it (previously `None`), and a negative `index` returns `None` (previously it wrapped to the last row).

**Pages:**

- `SurveyCreator.pages` / `SurveyForm.pages` — `Page` objects in schema order, exposing `name`, `title` (i18n-aware), `description`, `visible_if`, `is_visible`, `read_only`, `index`, `elements`, `questions`, `raw`.
- `get_page_by_name()` on both classes; `Element.page` back-reference, inherited by nested children from their container.
- A pages-less schema (top-level `elements`) is represented by a single implicit page named `page1`, so consumers have one code path.
- Pages are not elements: they never appear in `elements`, `all_elements`, `questions` or `all_element_paths`.

**Paths:**

- `Element.path` / `path_str` — structural position, unique across the survey (`contactPanel.phone`). Stable across parses and identical between a creator element and its form counterpart.
- `Element.input_path` / `input_path_str` — where the value actually lives in the submission data, as a list of `str` keys and `int` row indices (`['education', 0, 'year']`), directly usable to index the data. A `panel` is transparent to the data; a `paneldynamic` nests. `Element.get_value_from(data)` walks it.
- `all_element_paths` (alias `all_component_paths`) and `get_element_by_path()` on both classes.
- Supporting properties: `Element.nests_data`, `panel_index`, `in_repeating_context`, `registrable_children`.
- The vestigial, never-populated `survey_path` / `survey_input_path` attributes are renamed to `path` / `input_path` and are now computed.

**Panel instances:**

- A `SurveyCreator` holds a dynamic panel's *template* children (under `elements`, keyed by name). A `SurveyForm` now materialises one set of child elements per row of submission data, with values populated, exposed as `paneldynamic.panels` (a list of `PanelInstance`) and `get_panel(index)`.
- Instance children are registered by path only — `education[0].year`. Every row reuses the template's names, so a name-keyed map cannot represent them: they are deliberately absent from `all_elements` and `questions`, which continue to hold the paneldynamic itself.
- `Element.load()` gained `register_with_owner` / `register_with_parent` flags, used to keep repeating children out of the name-keyed maps.
- `Element.panel_instance` — the `PanelInstance` an element is a direct child of, or `None`. A row child's `parent` is the paneldynamic, so the instance is what holds its actual siblings.

**Text piping:**

- New `surveyjs.text` module with `interpolate_text(text, panel_index=None)`, exported as `surveyjs.interpolate_text`.
- `Element.title`, `Element.label` and `Element.description` substitute `{panelIndex}` with the **1-based** row number of the element's dynamic panel, matching SurveyJS. An element nested deeper than a direct row child (e.g. inside a panel inside a row) inherits its container's index.
- `PanelInstance.title` — the paneldynamic's `templateTitle` piped for that row. The paneldynamic itself sits outside any row and so cannot resolve `{panelIndex}`.
- Outside a repeating context there is no row number, so the placeholder is left exactly as authored (as on a `SurveyCreator`'s template children). Other pipes (`{question}`, `{row.field}`, `{panel.field}`) are untouched.
- `QuestionPaneldynamic.template_panel` — a blank `PanelInstance` materialised from the template as row 1, for rendering an empty form as one representative repeat. Built once on first access, from fresh child objects: stamping the template children the Creator keeps under `elements` would change their `path` from `passengers.first` to `passengers[0].first`.

**`inputType` parsing:**

- New `surveyjs.elements.inputtype` module: a single registry of parsers keyed by SurveyJS `inputType`, consulted by everything that carries one — a `text` question, a `multipletext` item, a matrix column.
- `value` parses `raw_value` according to the declared `inputType`: `date` → `date`, `datetime-local` → `datetime`, `time` → `time`, `month` → `date` (first of the month), `week` → `date` (Monday of the ISO week), `number` / `range` → `int` / `float`. Types with no parser (text, email, url, tel, password, color) pass their value through unchanged; a `None` or unparseable value yields `None`.
- `QuestionText` gains `to_time()`, `to_month()`, `to_week()` alongside the existing `to_number()`, `to_date()`, `to_datetime()`. These parse `raw_value` as a named type regardless of the declared `inputType`.
- `multipletext` items each carry their own `inputType` and parse independently: `question.item_values`, `question.raw_item_values`, `question.get_item(name)`, and an item's own `raw_value` / `value`. Items are `MultipleTextItem` objects exposing `name`, `title`, `input_type`, `is_required`, `placeholder`.
- `matrixdropdown` and `matrixdynamic` columns likewise: a column with `cellType: "text"` may declare an `inputType`, and every cell in it parses accordingly. Columns are `MatrixColumn` objects exposing `name`, `title`, `cell_type` (defaulting to the question's), `input_type`, `choices` (defaulting to the question's), `is_required`, and `parse(value)`. Both questions gain `column_names`, `column_count`, `get_column(name)`, `get_row_value(row)`, `get_row_raw_value(row)`, `get_cell_raw_value(row, column)`.
- `SurveyForm.get_raw_value(name)` alongside `get_value(name)`.
- Extension point for input types SurveyJS gains later: `surveyjs.register_input_type(input_type, parser)` registers or replaces a parser; `surveyjs.parse_input_value(input_type, value)` applies one directly. Registering a parser is all it takes to type a new `inputType` everywhere at once.
- `matrix` (single-select) is untouched: its rows and columns are choices, not cells, and carry no `inputType`. Container accessors that normalise shape rather than parse values — `rows_data`, `panels_data`, `column_values` — also keep returning submitted data unchanged.

**Fixes:**

- `Element.elements_on_same_line` raised `ValueError` for a materialised paneldynamic row child. It resolved siblings through `parent` — the paneldynamic, whose `elements` holds the *template* children rather than that row's — so the child was never found among them. Siblings now come from the child's `panel_instance`, leaving the parent path for ordinary nested elements and the owner path for top-level ones.
- `QuestionText.to_date()` handed a `datetime` returned it unchanged rather than narrowing it to a `date`, because `datetime` subclasses `date`. It now returns a `date`.
- `SurveyCreator` no longer constructs every panel child twice (once via `QuestionPanel.load_data`, then again via its own recursion, discarding the first copy).
- Two `paneldynamic`s may declare template children with the same name (e.g. `year`). Such names collide in the name-keyed `all_elements`, where the last one wins; `all_element_paths` keeps `jobs.year` and `school.year` distinct and reachable.
- Removed unused `deepcopy` / `OrderedDict` imports.

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
