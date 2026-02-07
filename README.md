# python-surveyjs-data

SurveyJS (JSON Form Builder) data API for Python.

For information about the SurveyJS project, see https://surveyjs.io

## Introduction

**python-surveyjs-data** is a Python package which loads and transforms
SurveyJS **Creator JSON** (survey schema) and **Form JSON** (submission data)
into **usable Python objects**.

Its main aim is to provide easy access to a Form's questions/fields,
also captured as **Python objects**, which makes this API very versatile and usable.

**Notes about terms:**
  - **SurveyCreator:** The Survey Creator (form builder) schema which is the design/blueprint of a Form.
  - **Form:** A filled-in Form, aka Form submission.
  - **Question:** Input (field) or layout element in the Survey and Form.

## Features

  - Compatible with Python 3.8 and later
  - Constructor of the **SurveyCreator** and **Form** class only requires
    the JSON (string or dict).
  - Get a Form object's Questions as usable Python objects
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
from surveyjs import SurveyCreator, Form

# survey_json is a SurveyJS Creator JSON schema (string or dict)
# form_json is a SurveyJS Form submission JSON (string or dict)

creator = SurveyCreator(survey_json)
form = Form(form_json, creator)

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

```
python -m pytest tests/ -v
```

### Run specific question type test

```
python -m pytest tests/test_question_text.py -v
```

## License

[MIT](LICENSE)
