# surveyjs (Python)

SurveyJS (JSON Form Builder) data API for Python.

For information about the SurveyJS project, see https://surveyjs.io

## Introduction

**surveyjs** is a Python package which loads and transforms
SurveyJS **Creator JSON** (survey schema) and **Form JSON** (submission data)
into **usable Python objects**.

Its main aim is to provide easy access to a SurveyJS Form's questions (fields, layout elements, etc.)
also captured as **Python objects**, which makes this API very versatile and usable.

**Notes about terms:**
  - **SurveyCreator:** The Survey Creator (form builder) schema which is the design of a Form.
  - **SurveyForm:** A filled-in Survey Form, aka Form response, submission.
  - **Question:** Input (field) and layout elements in SurveyJS (Creator and Form). Question is not a semantic term for a layout element (e.g. panel), but we follow the SurveyJS convention of calling all components "questions".

**Question types:**
 Source code (file prefix `question`): https://github.com/surveyjs/survey-library/tree/master/packages/survey-core/src

## Features

  - Compatible with Python 3.8 and later
  - Constructor of the **SurveyCreator** and **SurveyForm** class only requires
    the JSON (string or dict).
  - Get a SurveyForm object's Questions as usable Python objects
    e.g. datetime, boolean, list (for checkbox), dict (for matrix) etc.
  - Support for all SurveyJS question types
  - Open source (MIT License)

## Installation

```
pip install surveyjs
```

### Source Install

```
git clone <repo-url>
cd python-surveyjs
pip install -e .
```

## Usage Examples

```python
from surveyjs import SurveyCreator, SurveyForm

# survey_json is a SurveyJS Creator JSON schema (string or dict)
# form_json is a SurveyJS Form submission JSON (string or dict)

creator = SurveyCreator(survey_json)
form = SurveyForm(form_json, creator)

# Text question
print(form.input_questions['firstName'].label)
# 'First Name'

print(form.input_questions['firstName'].value)
# 'Bob'

# Checkbox question
print(form.input_questions['colors'].value)
# ['red', 'blue']

# Rating question
print(form.input_questions['satisfaction'].value)
# 4

# Boolean question
print(form.input_questions['agree'].value)
# True

# Matrix question
print(form.input_questions['quality'].value)
# {'affordable': 'good', 'does-what-it-claims': 'excellent'}

# Access by attribute
print(form.data.firstName.value)
# 'Bob'
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
