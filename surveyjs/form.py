# Copyright 2026 Nova Code (https://www.novaforms.io)
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
    Question (Element) objects with values populated from the submission.
    """

    def __init__(
        self,
        form_json,
        creator=None,
        creator_schema_json=None,
        lang="default",
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

        # Every element (question + layout) keyed by name — flat: also
        # includes elements nested inside panels.
        self.all_elements = OrderedDict()

        # Root (top-level) elements keyed by name; nested children are
        # reached via each container's `elements`.
        self.elements = OrderedDict()

        # Questions (fields) keyed by name
        self.questions = OrderedDict()

        # Every element keyed by internal id — flat (ids are unique across
        # the whole tree, so this registry is inherently global).
        self.all_element_ids = OrderedDict()

        # Load elements from survey schema + populate values from form data
        self.load_elements()

        # Create attribute-style accessor
        self._data = FormData(self)

    def set_creator_by_creator_schema_json(self):
        self.creator = SurveyCreator(
            self.creator_schema_json,
            language=self.lang,
        )

    # TODO?
    # @property
    # def elements(self):
    #     return self._elements

    # @elements.setter
    # def elements(self, elements):
    #     if isinstance(elements, OrderedDict):
    #         self._elements = elements
    #     else:
    #         self._elements = OrderedDict(elements)

    @property
    def data(self):
        """Attribute-style access to input questions."""
        return self._data

    @property
    def components(self):
        """Alias for `elements` (root, top-level)."""
        return self.elements

    @property
    def all_components(self):
        """Alias for `all_elements` (flat — includes nested)."""
        return self.all_elements

    @property
    def all_component_ids(self):
        """Alias for `all_element_ids` (flat — keyed by internal id)."""
        return self.all_element_ids

    @property
    def input_components(self):
        """ Alias for questions."""
        return self.questions

    def load_elements(self):
        """Load elements from the survey schema and populate values from
        form submission data.

        Only root elements are instantiated here; a container's nested
        children are built by its own `load_data` (with the container set as
        their parent). Every element is then registered into `all_elements`
        (flat) and `all_element_ids`, and root elements into `elements`,
        mirroring the Creator so `parent` distinguishes root from nested."""
        for creator_element in self.creator.elements.values():
            # Create a new element object (don't affect the Survey's element)
            element_obj = self.creator.get_element_object(creator_element.raw)
            element_obj.load(
                element_owner=self,
                parent=None,
                data=self.form,
                is_form=True,
            )
            self._register_element(element_obj)

    def _register_element(self, element_obj):
        """Register an element and all its descendants into the maps."""
        self.all_elements[element_obj.name] = element_obj
        if element_obj.parent is None:
            self.elements[element_obj.name] = element_obj
        if element_obj.id:
            self.all_element_ids[element_obj.id] = element_obj
        for child in element_obj.elements.values():
            self._register_element(child)

    def get_question_by_name(self, name):
        """Get a question by its name."""
        return self.questions.get(name)

    def get_value(self, name):
        """Get the value of a question by name."""
        question = self.questions.get(name)
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
        return self._form.questions.get(key)
