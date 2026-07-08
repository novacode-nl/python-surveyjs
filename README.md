[![Build Status](https://github.com/novacode-nl/python-surveyjs/actions/workflows/unittests.yml/badge.svg?branch=main)](https://github.com/novacode-nl/python-surveyjs/actions/workflows/unittests.yml/badge.svg?branch=main)
[![PyPI version](https://img.shields.io/pypi/v/surveyjs.svg)](https://pypi.org/project/surveyjs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# surveyjs (Python)

Python API for SurveyJS Creator (Form Builder) schema and Form response JSON.

For information about the SurveyJS project, see https://surveyjs.io

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
https://github.com/surveyjs/survey-library/tree/master/packages/survey-core/src \
The file prefix `question` indicates a question (field) class.

## Features

- Compatible with Python 3.8 and later.
- Constructor of the **SurveyCreator** and **SurveyForm** class only requires the JSON (string or dict) and an optional language code (e.g. 'en', 'fr', etc.) for localization of questions (e.g. titles and choices).
- Get a **SurveyForm object's Questions** as usable **Python objects** e.g. date, datetime, boolean, list (for checkbox), dict (for matrix) etc. Every question exposes both `raw_value` (exactly as submitted) and `value` (parsed according to its SurveyJS `inputType`).
- **Pages** and **paths**: iterate a survey's pages as objects, and address any element — however deeply nested — by a stable path such as `education[0].year`.
- **Dynamic panels** are materialized per row of submission data, with values populated.
- Supports a growing set of SurveyJS question types; additional types will be added over time and contributions via PRs are welcome.
- Open source (MIT License).

## Installation

The source code is currently hosted on GitHub at: https://github.com/novacode-nl/python-surveyjs

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

# Matrix question
form.questions['quality'].value
# {'affordable': 'good', 'does-what-it-claims': 'excellent'}

# Panel element
form.elements['personal_data']
# <QuestionPanel name=personal_data>
```

### Input types: `value` vs. `raw_value`

A question's `value` is its `raw_value` parsed according to the SurveyJS
`inputType`. Questions without an `inputType` are unaffected — the two are
equal.

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

Pages are objects. A schema with a top-level `elements` array and no `pages`
key is represented by a single implicit page, so there is only one code path.

```python
[page.name for page in creator.pages]
# ['personal', 'history']

creator.pages[0].title
# 'Personal'

list(creator.pages[0].elements)
# ['firstName', 'birthDate', 'contact']

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
#           {"name": "started", "cellType": "text", "inputType": "date"}]
jobs = form.questions['jobs']

jobs.get_column('started').input_type
# 'date'

jobs.get_cell_value(0, 'started')
# datetime.date(2020, 1, 6)

jobs.get_cell_raw_value(0, 'started')
# '2020-01-06'

jobs.get_row_value(0)
# {'employer': 'Nova Code', 'started': datetime.date(2020, 1, 6)}

# items: [{"name": "from", "inputType": "date"}]
form.questions['dates'].item_values
# {'from': datetime.date(2024, 7, 8)}
```

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

### Run specific component unittest

```
poetry run python -m unittest tests.test_question_ranking.TestQuestionRanking.test_choices
```

## License

[MIT](LICENSE)

Copyright 2026 Nova Code ([https://www.novaforms.io](https://www.novaforms.io))

---

Used in [Nova Forms](https://apps.odoo.com/apps/modules/19.0/formio) Form Builder & Forms App for [Odoo](https://www.odoo.com).

Developed and maintained by [Nova Code](https://www.novaforms.io).

Official [SurveyJS Partner](https://surveyjs.io/partner-solutions) [<img src="docs/surveyjs-partner-badge.svg" alt="Official SurveyJS Partner" width="120" align="middle">](https://surveyjs.io/partner-solutions)
