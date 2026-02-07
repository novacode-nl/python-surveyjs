# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

import json
import logging
from collections import OrderedDict
from copy import deepcopy

from surveyjs.questions.question import Question

logger = logging.getLogger(__name__)


class SurveyCreator:
    """
    Represents a SurveyJS Creator schema (the survey blueprint/design).

    Parses the survey JSON schema and creates Question objects for each
    question element found in the schema.

    Equivalent to the Builder class in python-formio-data.
    """

    def __init__(self, schema_json, language='en', i18n=None, **kwargs):
        """
        @param schema_json: SurveyJS Creator JSON schema (str or dict)
        @param language: Language code for translations (default: 'en')
        @param i18n: Translations dict
        """
        if isinstance(schema_json, dict):
            self.schema = schema_json
        else:
            self.schema = json.loads(schema_json)

        self.language = language
        self.i18n = i18n or {}

        # All questions (input + layout) keyed by name
        self.questions = OrderedDict()

        # Input-only questions keyed by name (no panels, html, image)
        self.input_questions = OrderedDict()

        # Questions keyed by internal id
        self.question_ids = OrderedDict()

        # Load all questions from the schema
        self.load_questions()

    @property
    def title(self):
        return self.schema.get('title', '')

    @property
    def description(self):
        return self.schema.get('description', '')

    @property
    def pages(self):
        return self.schema.get('pages', [])

    def load_questions(self):
        """Load questions from the schema, handling both pages-based and
        flat elements-based schemas."""
        pages = self.schema.get('pages')
        if pages:
            for page in pages:
                elements = page.get('elements', [])
                self._load_elements(elements)
        else:
            # Single page: elements at top level
            elements = self.schema.get('elements', [])
            self._load_elements(elements)

    def _load_elements(self, elements, parent=None):
        """Recursively load elements from the schema."""
        for element in elements:
            if 'type' not in element:
                continue

            question_obj = self.get_question_object(element)
            if not question_obj:
                continue

            question_obj.load(
                question_owner=self,
                parent=parent,
                data=None,
                is_form=False,
            )
            self.questions[question_obj.name] = question_obj

            if question_obj.id:
                self.question_ids[question_obj.id] = question_obj

            # Recurse into panel/page elements
            if element['type'] in ('panel', 'paneldynamic'):
                nested = element.get('elements', [])
                self._load_elements(nested, parent=question_obj)

    def get_question_class(self, element):
        """Dynamically load the question class based on the element type."""
        element_type = element.get('type')
        if not element_type:
            return None

        # Map SurveyJS types to class names
        type_map = {
            'text': ('text', 'textQuestion'),
            'comment': ('comment', 'commentQuestion'),
            'radiogroup': ('radiogroup', 'radiogroupQuestion'),
            'checkbox': ('checkbox', 'checkboxQuestion'),
            'dropdown': ('dropdown', 'dropdownQuestion'),
            'tagbox': ('tagbox', 'tagboxQuestion'),
            'boolean': ('boolean_q', 'booleanQuestion'),
            'rating': ('rating', 'ratingQuestion'),
            'ranking': ('ranking', 'rankingQuestion'),
            'imagepicker': ('imagepicker', 'imagepickerQuestion'),
            'signaturepad': ('signaturepad', 'signaturepadQuestion'),
            'expression': ('expression_q', 'expressionQuestion'),
            'file': ('file', 'fileQuestion'),
            'matrix': ('matrix', 'matrixQuestion'),
            'matrixdropdown': ('matrixdropdown', 'matrixdropdownQuestion'),
            'matrixdynamic': ('matrixdynamic', 'matrixdynamicQuestion'),
            'multipletext': ('multipletext', 'multipletextQuestion'),
            'panel': ('panel', 'panelQuestion'),
            'paneldynamic': ('paneldynamic', 'paneldynamicQuestion'),
            'html': ('html', 'htmlQuestion'),
            'image': ('image', 'imageQuestion'),
        }

        if element_type in type_map:
            module_name, cls_name = type_map[element_type]
        else:
            module_name = element_type
            cls_name = '%sQuestion' % element_type

        try:
            import_path = 'surveyjs.questions.%s' % module_name
            module = __import__(import_path, fromlist=[cls_name])
            cls = getattr(module, cls_name)
            return cls
        except (AttributeError, ModuleNotFoundError) as e:
            logger.warning(
                "Could not load question class for type '%s': %s. "
                "Falling back to base Question.", element_type, e
            )
            return Question

    def get_question_object(self, element):
        """Create a question object from an element dict."""
        cls = self.get_question_class(element)
        if cls is None:
            return None
        return cls(element, self, language=self.language, i18n=self.i18n)

    @property
    def form(self):
        """Placeholder form dict (always empty). Useful in contexts where
        a question owner's form is requested."""
        return {}
