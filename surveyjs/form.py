# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

import json
import logging
from collections import OrderedDict, defaultdict

from surveyjs.creator import SurveyCreator
from surveyjs.page import Page

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

        # Pages, in schema order — mirrors the creator's pages, but holding
        # this form's element objects. Pages are not elements: they never
        # appear in the element registries below.
        self.pages = []

        # Every element (question + layout) keyed by name — flat: also
        # includes elements nested inside panels.
        self.all_elements = OrderedDict()

        # Root (top-level) elements keyed by name; nested children are
        # reached via each container's `elements`.
        self.elements = OrderedDict()

        # Questions (fields) keyed by name
        self.questions = OrderedDict()

        # Every element keyed by dotted path — flat. Paths are unique across
        # the whole tree (unlike names, which collide between the template
        # children of two paneldynamics), and match the creator's paths.
        self.all_element_paths = OrderedDict()

        # Load elements from survey schema + populate values from form data
        self.load_elements()

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
        """Alias for `elements` (root, top-level)."""
        return self.elements

    @property
    def all_components(self):
        """Alias for `all_elements` (flat — includes nested)."""
        return self.all_elements

    @property
    def all_component_paths(self):
        """Alias for `all_element_paths` (flat — keyed by dotted path)."""
        return self.all_element_paths

    @property
    def input_components(self):
        """ Alias for questions."""
        return self.questions

    def load_elements(self):
        """Load pages and elements from the survey schema and populate values
        from form submission data.

        Only root elements are instantiated here; a container's nested
        children are built by its own `load_data` (with the container set as
        their parent). Every element is then registered into `all_elements`
        (flat) and `all_element_paths`, and root elements into `elements`,
        mirroring the Creator so `parent` distinguishes root from nested.

        Pages mirror the creator's pages one-for-one, but hold this form's
        element objects rather than the creator's."""
        for creator_page in self.creator.pages:
            page = Page(
                creator_page.raw,
                self,
                index=creator_page.index,
                language=self.lang,
                i18n=self.creator.i18n,
                implicit=creator_page.implicit,
            )
            self.pages.append(page)

            for creator_element in creator_page.elements.values():
                # Create a new element object (don't affect the Survey's element)
                element_obj = self.creator.get_element_object(creator_element.raw)
                element_obj.load(
                    element_owner=self,
                    parent=None,
                    data=self.form,
                    is_form=True,
                )
                page.add_element(element_obj)
                self._register_element(element_obj)

    def get_page_by_name(self, name):
        """Get a page by its name."""
        for page in self.pages:
            if page.name == name:
                return page
        return None

    def _register_element(self, element_obj):
        """Register an element and all its descendants into the maps.

        Elements inside a materialised panel instance are filed by path only:
        every row reuses the template's names, so a name-keyed map cannot hold
        them (which row would `all_elements['year']` be?)."""
        self.all_element_paths[element_obj.path_str] = element_obj

        if not element_obj.in_repeating_context:
            self.all_elements[element_obj.name] = element_obj
            if element_obj.parent is None:
                self.elements[element_obj.name] = element_obj

        for child in element_obj.registrable_children:
            self._register_element(child)

    def get_element_by_path(self, path):
        """Get an element by its path — a dotted string or a list of names."""
        if not isinstance(path, str):
            path = '.'.join(path)
        return self.all_element_paths.get(path)

    def get_question_by_name(self, name):
        """Get a question by its name."""
        return self.questions.get(name)

    def get_value(self, name):
        """Get a question's value by name, parsed per its `inputType`."""
        question = self.questions.get(name)
        if question:
            return question.value
        return None

    def get_raw_value(self, name):
        """Get a question's value by name, exactly as submitted."""
        question = self.questions.get(name)
        if question:
            return question.raw_value
        return None

    def validation_errors(self):
        """Collect validation errors across every input question.

        Mirrors formio-data's ``Form.validation_errors``: asks each question
        for its own errors and aggregates them, keyed by question
        name. A question with no errors is omitted, so an empty result means
        the whole submission is valid.

        @return dict: {question_name: {error_type: message}}. A question that
            returns a list of errors is stored as that list.
        """
        errors = defaultdict(dict)
        for name, question in self.questions.items():
            question_errors = question.validation_errors()
            if isinstance(question_errors, dict):
                for error_type, val in question_errors.items():
                    errors[name].update({error_type: val})
            elif isinstance(question_errors, list) and question_errors:
                errors[name] = question_errors
        return dict(errors)


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
