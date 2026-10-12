[![Build Status](https://github.com/novacode-nl/python-surveyjs/actions/workflows/unittests.yml/badge.svg?branch=main)](https://github.com/novacode-nl/python-surveyjs/actions/workflows/unittests.yml/badge.svg?branch=main)
[![PyPI version](https://img.shields.io/pypi/v/surveyjs.svg)](https://pypi.org/project/surveyjs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# surveyjs (Python)

Python API for SurveyJS Creator (Form Builder) schema and Form response JSON.

For information about the SurveyJS project, see <https://surveyjs.io>

## Introduction

**surveyjs** is a Python package that parses and transforms **SurveyJS Creator (Form Builder) JSON schema** and **Form response JSON** into **usable Python objects**.

Its main aim is to provide easy access to a SurveyJS Form's questions (fields, layout elements, etc.) also captured as **Python objects**, which makes this API very versatile and usable.

**Notes about terms:**
- **SurveyCreator:** The Survey Creator (form builder) that defines the structure and design of a Form, with a schema in JSON format.
- **SurveyForm:** A filled-in or completed survey form, i.e. a form response or submission, with data in JSON format.
- **Question:** Represents a form field, ranging from simple input types (e.g. text, checkbox, rating) to more complex elements (e.g. matrix).
- **Layout:** A structural element such as a page, panel, or dynamic panel that can contain other elements, including questions and nested layouts.
- **Element:** The base concept for both Question and Layout elements in SurveyJS.

**SurveyJS question and layout classes (source code):**\
<https://github.com/surveyjs/survey-library/tree/master/packages/survey-core/src> \
The file prefix `question` indicates a question (field) class.

## Features

- Compatible with Python 3.8 and later.
- Constructor of the **SurveyCreator** and **SurveyForm** class only requires the JSON (string or dict) and an optional language code (e.g. 'en', 'fr', etc.).
- **Translations**: every displayed text (titles, descriptions, choices, boolean labels, error messages, …) is translated, from SurveyJS localizable strings and/or an `i18n` map (see [Translations](#translations)).
- Get a **SurveyForm object's Questions** as usable **Python objects** e.g. date, datetime, boolean, list (for checkbox), dict (for matrix) etc. Every question exposes both `raw_value` (exactly as submitted) and `value` (parsed according to its SurveyJS type and `inputType`).
- **Pages** and **paths**: iterate a survey's pages as objects, and address any element — however deeply nested — by a stable path such as `education[0].year`.
- **Dynamic panels** are materialized per row of submission data, with values populated.
- **Matrix cells are questions**: a column's `cellType` decides a cell's class, so a dropdown cell resolves its own choices and a date cell parses its own value.
- **Validation**: `validation_errors()` on a whole form or a single question, covering the `isRequired` flag and SurveyJS's `validators` array (numeric, text, answercount, regex, email).
- **Extensible**: register an `inputType` parser, a validator, or a question class of your own (see [Extending](#extending)).
- Supports [23 SurveyJS question types](#supported-question-types); additional types will be added over time and contributions via PRs are welcome.
- Open source (MIT License).

## Supported question types

Each type below is implemented by its own class in `surveyjs/elements/` and covered
by its own test module. A type that is not listed still loads: it falls back to the
base `Element`, so its `raw_value`, `title` and position in the tree are available;
only the behaviour specific to that type is missing.

| Category | Types |
|---|---|
| Text input | `text`, `comment`, `multipletext` |
| Choice | `dropdown`, `checkbox`, `radiogroup`, `tagbox`, `buttongroup`, `imagepicker`, `boolean`, `ranking` |
| Scale | `rating`, `slider` |
| Matrix | `matrix`, `matrixdropdown`, `matrixdynamic` |
| Layout | `panel`, `paneldynamic`, `html`, `image` |
| Other | `file`, `signaturepad`, `expression` |

Missing a type you need? [Contributions](CONTRIBUTING.md) are welcome.

## Installation

The source code is currently hosted on GitHub at: <https://github.com/novacode-nl/python-surveyjs>

### PyPI - Python Package Index

Binary installers for the latest released version are available at the [Python Package Index](https://pypi.python.org/pypi/surveyjs).

```sh
pip install surveyjs
```

### Source Install with pip

```sh
git clone git@github.com:novacode-nl/python-surveyjs.git
cd python-surveyjs
pip install -e .
```

### Source Install with Poetry (recommended)

```sh
git clone git@github.com:novacode-nl/python-surveyjs.git
cd python-surveyjs
poetry install
```

## Using direnv

You can use [nixpkgs](https://nixos.org/) to run a self-contained Python environment without any additional setup.\
Once you've installed nixpkgs, switch into the directory and type "nix-shell" to get a shell from which the correct Python with packages is available.

If you're using [direnv](https://direnv.net/), use `direnv allow` after changing into the project directory and you're good to go.\
Also consider [nix-direnv](https://github.com/nix-community/nix-direnv) to speed up the experience (it can re-use a cached local installation).

## Usage Examples

Every snippet below is executed by [`tests/test_readme_examples.py`](tests/test_readme_examples.py)
against the same demo survey, so an example that stopped being true fails the build
rather than misleading you. Change a snippet, change its test.

### Questions and values

```python
from surveyjs import SurveyCreator, SurveyForm

# creator_json is a SurveyJS Creator JSON schema (string or dict)
# form_json is a SurveyJS Form submission JSON (string or dict)

creator = SurveyCreator(creator_json)
form = SurveyForm(form_json, creator)

# Text question
form.questions['firstName'].label
# 'First Name'

form.questions['firstName'].value
# 'Bob'

# Checkbox question
form.questions['colors'].value
# ['red', 'blue']

# Rating question
form.questions['satisfaction'].value
# 4

# Boolean question
form.questions['agree'].value
# True

# Date question (inputType 'date')
form.questions['birthDate'].value
# datetime.date(1985, 6, 14)

# Datetime question (inputType 'datetime-local')
form.questions['appointment'].value
# datetime.datetime(2024, 3, 15, 13, 45)

# Matrix question
form.questions['quality'].value
# {'affordable': 'good', 'does-what-it-claims': 'excellent'}

# Panel element
form.elements['personal_data']
# <QuestionPanel name=personal_data>
```

### Input types: `value` vs. `raw_value`

A question's `raw_value` is its answer exactly as submitted; `value` is that
answer as a Python object. For a text question, `value` is parsed according to
its SurveyJS `inputType`:

```python
# {"type": "text", "name": "birthDate", "inputType": "date"}

form.questions['birthDate'].value
# datetime.date(1985, 6, 14)

form.questions['birthDate'].raw_value
# '1985-06-14'
```

`date` yields a `date`, `datetime-local` a `datetime`, `time` a `time`,
`month` a `date` (first of the month), `week` a `date` (Monday of the ISO
week), and `number`/`range` an `int`/`float`. Types with no parser (text,
email, url, …) pass through unchanged.

A **boolean** question's `value` is always `True`, `False` or `None`, whatever
its `valueTrue`/`valueFalse`; `value_text` is the matching label:

```python
# {"type": "boolean", "name": "consent", "valueTrue": "agreed", "valueFalse": "declined"}

form.questions['consent'].raw_value
# 'agreed'

form.questions['consent'].value
# True

form.questions['consent'].value_text
# 'Yes'
```

The questions that hold other questions — `multipletext`, `matrixdynamic`,
`matrixdropdown` and `paneldynamic` — return a parsed copy from `value`: a new
dict or list with the same keys and rows as `raw_value`, each value inside
parsed by its own item, column or question (see
[Dynamic panels](#dynamic-panels) and
[Matrix columns and multiple-text items](#matrix-columns-and-multiple-text-items)).
Other questions (dropdown, checkbox, rating, …) submit JSON values that are
already Python objects, so their `value` equals `raw_value`.

`value` is read-only — assign `raw_value` instead. If a submitted value cannot
be parsed, `value` is `None` while `raw_value` keeps the original, which is how
you tell a malformed submission from an empty one.

To register an `inputType` of your own (or override a built-in):

```python
from datetime import timedelta
from surveyjs import register_input_type

register_input_type('duration', lambda v: timedelta(seconds=int(v)))

form.questions['elapsed'].value
# datetime.timedelta(seconds=90)
```

### Pages

Both **SurveyCreator** and **SurveyForm** have a `pages` property: a list of
`Page` objects in schema order. They mirror each other — same names, same
titles, same order — but hold different element objects. A creator's page
holds the *schema* elements (no submitted values); a form's page holds that
form's elements, with values populated.

A schema with a top-level `elements` array and no `pages` key is represented
by a single implicit page named `page1`, so there is only one code path.

```python
# the same pages on both, in schema order
[page.name for page in creator.pages]
# ['personal', 'history']

[page.name for page in form.pages]
# ['personal', 'history']

form.pages[0].title
# 'Personal'

# look a page up by name, on either class
form.get_page_by_name('history')
# <Page name=history>
```

A page's root elements are an `OrderedDict` of Element objects keyed by name —
the same shape as `creator.elements` / `form.elements`.

```python
form.pages[0].elements['firstName']
# <QuestionText name=firstName input_type=text>

list(form.pages[0].elements.values())
# [<QuestionText name=firstName input_type=text>,
#  <QuestionText name=birthDate input_type=date>,
#  <QuestionText name=appointment input_type=datetime-local>,
#  <QuestionPanel name=contact>]

list(form.pages[0].elements)             # dict keys, i.e. the element names
# ['firstName', 'birthDate', 'appointment', 'contact']

# .questions is the same, filtered to input questions (no panel/html/image)
list(form.pages[0].questions)
# ['firstName', 'birthDate', 'appointment']
```

Read values from a **form** page — a creator page describes the schema, so its
elements have no submitted value:

```python
form.pages[0].elements['firstName'].value
# 'Bob'

form.pages[0].elements['birthDate'].value
# datetime.date(1985, 6, 14)

creator.pages[0].elements['birthDate'].value
# None      (a schema has no submission data)

# every element knows its page
form.questions['birthDate'].page.name
# 'personal'
```

### Paths

`path` is an element's position in the survey tree; `input_path` is where its
value lives in the submission data. They differ because a `panel` groups
elements visually without nesting their data.

```python
form.all_elements['phone'].path_str
# 'contact.phone'          (inside the 'contact' panel)

form.all_elements['phone'].input_path
# ['phone']                (panels are transparent to the data)

form.get_element_by_path('contact.phone').value
# '+31 6 1234 5678'
```

### Dynamic panels

A `SurveyCreator` holds a dynamic panel's *template*. A `SurveyForm`
materializes one set of child elements per row of submission data, with values
populated.

```python
education = form.questions['education']

education.panels
# [<PanelInstance name=education[0]>]

education.panels[0]['graduated'].value
# datetime.date(2015, 5, 30)

education.get_panel_value(0, 'school')
# 'MIT'

# the whole value: a parsed copy of raw_value
education.value
# [{'school': 'MIT', 'graduated': datetime.date(2015, 5, 30)}]

education.raw_value
# [{'school': 'MIT', 'graduated': '2015-05-30'}]

# rows are addressable by path
form.get_element_by_path('education[0].graduated').input_path
# ['education', 0, 'graduated']    -> data['education'][0]['graduated']
```

Because each row reuses the template's names, instance children are addressed
by path rather than by name: they are deliberately absent from `questions` and
`all_elements`.

### Matrix columns and multiple-text items

A matrix column with `cellType: "text"` may declare its own `inputType`, and so
may a `multipletext` item. Each parses independently.

```python
# columns: [{"name": "employer"},
#           {"name": "started", "cellType": "text", "inputType": "date"},
#           {"name": "role", "cellType": "dropdown", "choices": [...]}]
jobs = form.questions['jobs']

jobs.get_column('started').input_type
# 'date'

jobs.get_cell_value(0, 'started')
# datetime.date(2020, 1, 6)

jobs.get_cell_raw_value(0, 'started')
# '2020-01-06'

jobs.get_row_value(0)
# {'employer': 'Nova Code', 'started': datetime.date(2020, 1, 6), 'role': 'dev'}

# the whole value: every row, each cell parsed — raw_value stays as submitted
jobs.value
# [{'employer': 'Nova Code', 'started': datetime.date(2020, 1, 6), 'role': 'dev'}]

jobs.raw_value
# [{'employer': 'Nova Code', 'started': '2020-01-06', 'role': 'dev'}]

# items: [{"name": "from", "inputType": "date"}]
form.questions['dates'].item_values
# {'from': datetime.date(2024, 7, 8)}

form.questions['dates'].value
# {'from': datetime.date(2024, 7, 8)}

form.questions['dates'].raw_value
# {'from': '2024-07-08'}
```

### Matrix cells as questions

A column's `cellType` *is* a question type, so on a **SurveyForm** every cell of a
submitted row is built as a question of that type. That is what gives a cell the
behaviour of its type: a dropdown cell resolves what its value means, where
`get_cell_value()` only ever types the value by the column's `inputType`.

```python
jobs.get_cell(0, 'role')
# <QuestionDropdown name=role>

jobs.get_cell(0, 'role').value
# 'dev'

jobs.get_cell(0, 'role').value_text      # what a dropdown cell knows and a value does not
# 'Developer'

list(jobs.cells(0).values())             # one row of cells, in column order
# [<QuestionText name=employer input_type=text>,
#  <QuestionText name=started input_type=date>,
#  <QuestionDropdown name=role>]

list(jobs.cells(0))                      # dict keys, i.e. the column names
# ['employer', 'started', 'role']

list(jobs.rows_cells)                    # every submitted row, by row key
# [0]
```

A **SurveyCreator** materializes no cells: it has no submission, so it has no rows.
The column as the element definition its cells are built from is `cell_raw`:

```python
jobs.get_column('started').cell_raw
# {'name': 'started', 'cellType': 'text', 'inputType': 'date', 'type': 'text'}
```

Like a dynamic panel's row children, cells are registered by **path** and never by
name — a column name repeats in every row:

```python
form.get_element_by_path('jobs[0].role').value_text
# 'Developer'

jobs.get_cell(0, 'started').input_path
# ['jobs', 0, 'started']       -> data['jobs'][0]['started']

'role' in form.questions
# False
```

A `matrixdropdown` keys its rows by **name** rather than position, and those names
are addressable the same way:

```python
# rows: [{"value": "marketing", "text": "Marketing"}]
form.questions['budget'].row_names
# ['marketing']

form.get_element_by_path('budget[marketing].status').value_text
# 'Done'

form.get_element_by_path('budget[marketing].status').input_path
# ['budget', 'marketing', 'status']
```

`row_key` is which row of a repeating container an element belongs to — an int
where the data is a list of rows (a dynamic panel, a dynamic matrix), the row's
name for a `matrixdropdown`. `panel_index` is the dynamic-panel spelling of the
same value, and keeps working.

Reading a matrix as values still works without cells: `value`,
`get_row_value()` and `get_cell_value()` parse, `rows_data` and the `*_raw_value`
accessors return the submission as is. Cells cost one
element per cell of a submitted matrix, on the form path only.

### Validation

`validation_errors()` reports what a submission gets wrong. On a **SurveyForm** it
collects errors across every input question, keyed by question name; an empty dict
means the whole submission is valid.

```python
# {"type": "text", "name": "email", "title": "Email", "isRequired": true,
#  "validators": [{"type": "email"}]}
# {"type": "text", "name": "age", "title": "Age", "inputType": "number",
#  "validators": [{"type": "numeric", "minValue": 18}]}

form = SurveyForm({'email': 'not-an-address', 'age': '16'}, creator)

form.validation_errors()
# {'email': {'email': 'Please enter a valid e-mail address.'},
#  'age': {'numeric': "The 'Age' should be at least 18"}}
```

The result is a plain dict, so reading an absent key raises instead of silently
inserting an empty entry. A single question answers for itself, keyed by error
type:

```python
form.questions['age'].validation_errors()
# {'numeric': "The 'Age' should be at least 18"}

form.questions['age'].is_empty()
# False
```

Two kinds of rule are checked, and they never collide because they apply to
opposite states:

- the **`isRequired`** flag, keyed `required`, only when the answer is empty;
- each entry in the **`validators`** array, keyed by its `type`, only when the
  answer is non-empty, matching SurveyJS, which passes validators on empty input.

```python
SurveyForm({'email': ''}, creator).validation_errors()
# {'email': {'required': 'Email is required'}}
```

Supported validator types are `numeric`, `text`, `answercount`, `regex` and
`email`, with SurveyJS's own default messages; a validator's own `text` overrides
the message. An unknown type is skipped rather than guessed at. That includes
`expression`, which needs a SurveyJS expression runtime this library does not
carry, so its rules are ignored rather than mis-evaluated. To add a type, see
[Extending](#extending).

### Translations

Every text a respondent reads is translated: titles, descriptions,
placeholders, choice texts (and so `value_text`), boolean labels, button
texts, and validation messages. SurveyJS offers two ways to translate, and both
apply, in this order:

1. **Localizable strings** in the schema — a dict keyed by locale. The
   survey's language is picked, else `default`, else the first locale given.
2. An **`i18n` map**, `{language: {source text: translation}}`, passed to the
   `SurveyCreator`. It translates the text from step 1; a text it does not
   list is kept as is.

```python
# {"type": "boolean", "name": "agree",
#  "title": {"default": "I agree", "fr": "J'accepte"}},
# {"type": "dropdown", "name": "color", "choices": ["Red", "Blue"]}
i18n = {'fr': {'Yes': 'Oui', 'No': 'Non', 'Red': 'Rouge', 'Blue': 'Bleu'}}

creator = SurveyCreator(creator_json, language='fr', i18n=i18n)
form = SurveyForm(form_json, creator)

form.questions['agree'].title
# "J'accepte"

form.questions['agree'].value_text
# 'Oui'

form.questions['color'].value_text
# 'Rouge'
```

A form uses its creator's `language` unless you pass `lang`, which then
applies to the whole form — pages, questions, and everything nested in panels,
dynamic panels and matrix cells. The creator keeps its own language, so one
creator can serve forms in several languages:

```python
form_en = SurveyForm(form_json, creator, lang='default')

form_en.questions['agree'].title
# 'I agree'

form_en.questions['agree'].value_text
# 'Yes'
```

## Extending

Three registration points let you teach the library something it does not already
know, or override what it does.

### Input types

`register_input_type` adds or replaces the parser behind a question's `inputType`
(see [Input types](#input-types-value-vs-raw_value) above).

### Validators

`register_validator` adds or replaces the function behind a validator `type`. It
receives the question's parsed `value`, the rule dict and the element, and returns
an error message, or `None` when the value passes. Usable as a decorator:

```python
from surveyjs.elements.validators import register_validator

@register_validator('creditcard')
def _creditcard(value, rule, element):
    return None if luhn_ok(value) else 'Invalid card number.'
```

### Question classes

`element_class_mapping` decides which class a question type is built as — for every
question of that type, including one inside a matrix cell or a dynamic panel row.
Pass a class, or a dotted path to one:

```python
from surveyjs import SurveyCreator
from surveyjs.elements.text import QuestionText

class MyText(QuestionText):
    @property
    def value(self):
        return (super().value or '').strip()

creator = SurveyCreator(creator_json, element_class_mapping={'text': MyText})

# or by dotted path, resolved on load
creator = SurveyCreator(creator_json, element_class_mapping={'text': 'myapp.widgets.MyText'})
```

A type with no mapping resolves by convention to `surveyjs.elements.<type>.Question<Type>`.

## Unit Tests

### Run all tests

From toplevel directory:
```
poetry run python -m unittest
```

### Run specific (questions) unittests

All questions, from toplevel directory:

```
poetry run python -m unittest tests/test_question_*.py
```

Nested questions (complexity), from toplevel directory:

```
poetry run python -m unittest tests/test_nested_questions.py
```

### Run specific element/question unittest

```
poetry run python -m unittest tests.test_question_ranking.TestQuestionRanking.test_choices
```

## Contributing

Contributions are welcome — a new question type, a validator, a bug fix. See
[CONTRIBUTING.md](CONTRIBUTING.md) for how to set up, test and submit a change.

Note that the [Usage Examples](#usage-examples) are executed as tests: a change
that alters documented output must update
[`tests/test_readme_examples.py`](tests/test_readme_examples.py) alongside the
README.

## Changelog

Release notes are in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)

Copyright 2026 Nova Code ([https://www.novaforms.io](https://www.novaforms.io))

---

Developed and maintained by [Nova Code](https://www.novaforms.io).

Official [SurveyJS Partner](https://surveyjs.io/partner-solutions) [<img src="docs/surveyjs-partner-badge.svg" alt="Official SurveyJS Partner" width="120" align="middle">](https://surveyjs.io/partner-solutions)
