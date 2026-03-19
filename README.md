# surveyjs (Python)

Python object API for SurveyJS Creator (form builder) and Form (response, submission) data.

For information about the SurveyJS project, see https://surveyjs.io

## Introduction

**surveyjs** is a Python package which loads and transforms SurveyJS **Creator JSON** (survey schema) and **Form JSON** (submission data) into **usable Python objects**.

Its main aim is to provide easy access to a SurveyJS Form's questions (fields, layout elements, etc.) also captured as **Python objects**, which makes this API very versatile and usable.

**Notes about terms:**
- **SurveyCreator:** The Survey Creator (form builder) that defines the structure and design of a Form, with a schema in JSON format.
- **SurveyForm:** A filled-in or completed survey form, i.e. a form response or submission, with data in JSON format.
- **Question:** Represents a form field, ranging from simple input types (e.g. text, checkbox, rating) to more complex elements (e.g. matrix).
- **Layout:** A structural element such as a page, panel, or dynamic panel that can contain other elements, including questions and nested layouts.
- **Element:** The base concept for both Question and Layout elements in SurveyJS.

**Question and layout classes (source code):**\
https://github.com/surveyjs/survey-library/tree/master/packages/survey-core/src \
The file prefix `question` indicates a question (field) class.

## Features

- Compatible with Python 3.8 and later.
- Constructor of the **SurveyCreator** and **SurveyForm** class only requires the JSON (string or dict) and an optional language code (e.g. 'en', 'fr', etc.) for localization of questions (e.g. titles and choices).
- Get a SurveyForm object's Questions as usable Python objects e.g. datetime, boolean, list (for checkbox), dict (for matrix) etc.
- Support for all SurveyJS question types.
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

```python
from surveyjs import SurveyCreator, SurveyForm

# survey_json is a SurveyJS Creator JSON schema (string or dict)
# form_json is a SurveyJS Form submission JSON (string or dict)

creator = SurveyCreator(survey_json)
form = SurveyForm(form_json, creator)

# Text question
print(form.questions['firstName'].label)
# 'First Name'

print(form.questions['firstName'].value)
# 'Bob'

# Checkbox question
print(form.questions['colors'].value)
# ['red', 'blue']

# Rating question
print(form.questions['satisfaction'].value)
# 4

# Boolean question
print(form.questions['agree'].value)
# True

# Matrix question
print(form.questions['quality'].value)
# {'affordable': 'good', 'does-what-it-claims': 'excellent'}

# Panel element
print(form.elements['personal_data'])
# <QuestionPanel>
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
