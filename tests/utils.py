# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def readfile(filename):
    """Read a file from the test data directory and return its contents."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r') as f:
        return f.read()


def readjson(filename):
    """Read a JSON file from the test data directory and return a dict."""
    return json.loads(readfile(filename))


def load_creator():
    """Load the test survey schema."""
    from surveyjs import SurveyCreator
    schema = readjson('test_survey_schema.json')
    return SurveyCreator(schema)


def load_form():
    """Load the test form with survey schema."""
    from surveyjs import SurveyCreator, Form
    schema = readjson('test_survey_schema.json')
    form_json = readjson('test_survey_form.json')
    creator = SurveyCreator(schema)
    return Form(form_json, creator=creator)
