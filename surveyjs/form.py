# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

import json
import logging
from collections import OrderedDict

from surveyjs import SurveyCreator

logger = logging.getLogger(__name__)


class SurveyForm:
    """
    Represents a filled-in SurveyJS form (submission data).

    Parses the form submission JSON against a SurveyCreator schema and creates
    Question objects with values populated from the submission.

    Equivalent to the Form class in python-formio-data.
    """

    def __init__(
        self,
        form_json,
        creator=None,
        creator_schema_json=None,
        lang="en",
        **kwargs
    ):
        """
        @param form_json: SurveyJS Form submission JSON (str or dict)
        @param creator: A SurveyCreator instance
        @param creator_schema_json: SurveyCreator schema JSON (str or dict)
            Alternative to providing a SurveyCreator instance.
        @param lang: Language code for translations (default: 'en')
        """

        if creator and creator_schema_json:
            raise Exception(
                "Constructor accepts either creator or creator_schema_json, not both."
            )

        if isinstance(form_json, dict):
            self.form = form_json
        else:
            self.form = json.loads(form_json)

        self.creator = creator
        self.creator_schema_json = creator_schema_json

        if self.creator is None and self.creator_schema_json:
            self.creator = SurveyCreator(self.creator_schema_json)

        if self.creator:
            if not isinstance(self.creator, SurveyCreator):
                raise TypeError("creator must be a SurveyCreator instance")
        elif self.creator_schema_json:
            assert isinstance(self.creator_schema_json, str)

        else:
            raise Exception(
                "Provide either the argument: creator or creator_schema_json."
            )

        self.lang = lang
        # defaults to English (en) date/time format
        self.date_format = kwargs.get('date_format', '%m/%d/%Y')
        self.time_format = kwargs.get('time_format', '%H:%M:%S')

        # All questions (input + layout) keyed by name
        self.questions = OrderedDict()

        # Input-only questions keyed by name
        self.input_questions = OrderedDict()

        # Questions keyed by id
        self.question_ids = {}

        # Load questions from survey schema + populate values from form data
        self.load_questions()

        # Create attribute-style accessor
        self._data = FormData(self)

    def set_creator_by_creator_schema_json(self):
        self.creator = SurveyCreator(
            self.creator_schema_json,
            language=self.lang,
        )

    @property
    def data(self):
        """Attribute-style access to input questions."""
        return self._data

    @property
    def components(self):
        """ Alias for questions, including both input and layout questions."""
        return self.questions

    @property
    def input_components(self):
        """ Alias for questions, including input queastions."""
        return self.input_questions

    def load_questions(self):
        """Load questions from the survey schema and populate values from
        form submission data."""
        for key, creator_question in self.creator.questions.items():
            # Create a new question object (don't affect the Survey's question)
            question_obj = self.creator.get_question_object(creator_question.raw)
            question_obj.load(
                question_owner=self,
                parent=None,
                data=self.form,
                is_form=True,
            )
            self.questions[key] = question_obj

            if question_obj.id:
                self.question_ids[question_obj.id] = question_obj

    def get_question_by_name(self, name):
        """Get a question by its name."""
        return self.input_questions.get(name)

    def get_value(self, name):
        """Get the value of a question by name."""
        question = self.input_questions.get(name)
        if question:
            return question.value
        return None


class FormData:
    """Provides attribute-style access to form input questions.

    Example:
        form.data.firstName.value  # => 'Bob'
    """

    def __init__(self, form):
        self._form = form

    def __getattr__(self, key):
        if key.startswith('_'):
            return super().__getattribute__(key)
        return self._form.input_questions.get(key)
