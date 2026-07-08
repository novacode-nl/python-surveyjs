# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

import json
import logging
from collections import OrderedDict

from surveyjs.elements.element import Element
from surveyjs.page import Page

logger = logging.getLogger(__name__)


class SurveyCreator:
    """
    Represents a SurveyJS Creator schema (the survey blueprint/design).

    Parses the survey JSON schema and creates Element objects for each
    element found in the schema.
    """

    def __init__(
        self,
        schema_json,
        language='default',
        i18n=None,
        element_class_mapping={},
        **kwargs
    ):
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

        self.element_class_mapping = element_class_mapping

        # Pages, in schema order. Pages are not elements: they never appear
        # in the element registries below.
        self.pages = []

        # Every element (question + layout) keyed by name — flat: also
        # includes elements nested inside panels.
        self.all_elements = OrderedDict()

        # Root (top-level) elements keyed by name; nested children are
        # reached via each container's `elements`.
        self.elements = OrderedDict()

        # Questions (fields) keyed by name (no panels, html, image)
        self.questions = OrderedDict()

        # Every element keyed by dotted path — flat. Paths are unique across
        # the whole tree (unlike names, which collide between the template
        # children of two paneldynamics), so this registry is lossless.
        self.all_element_paths = OrderedDict()

        # Load all elements from the schema
        self.load_elements()

    @property
    def title(self):
        return self.schema.get('title', '')

    @property
    def description(self):
        return self.schema.get('description', '')

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
        return self.questions

    def load_elements(self):
        """Load pages and their elements from the schema, handling both
        pages-based and flat elements-based schemas."""
        pages_raw = self.schema.get('pages')
        implicit = not pages_raw
        if implicit:
            # Pages-less schema: elements at top level become one implicit page.
            pages_raw = [{'elements': self.schema.get('elements', [])}]

        for index, page_raw in enumerate(pages_raw):
            page = Page(
                page_raw,
                self,
                index=index,
                language=self.language,
                i18n=self.i18n,
                implicit=implicit,
            )
            self.pages.append(page)
            self._load_elements(page_raw.get('elements', []), page=page)

    def get_page_by_name(self, name):
        """Get a page by its name."""
        for page in self.pages:
            if page.name == name:
                return page
        return None

    def get_element_by_path(self, path):
        """Get an element by its path — a dotted string or a list of names."""
        if not isinstance(path, str):
            path = '.'.join(path)
        return self.all_element_paths.get(path)

    def _load_elements(self, elements, parent=None, page=None):
        """Recursively load elements from the schema."""
        for element in elements:
            if 'type' not in element:
                continue

            element_obj = self.get_element_object(element)
            if not element_obj:
                continue

            element_obj.load(
                element_owner=self,
                parent=parent,
                data=None,
                is_form=False,
            )
            self.all_elements[element_obj.name] = element_obj
            self.all_element_paths[element_obj.path_str] = element_obj
            if parent is None:
                self.elements[element_obj.name] = element_obj
                if page is not None:
                    # Back-links element -> page; nested children inherit it
                    # through their parent container.
                    page.add_element(element_obj)

            # Recurse into panel/paneldynamic nested elements. Note that
            # paneldynamic stores its children under ``templateElements``
            # (the per-row template), not ``elements``.
            if element['type'] == 'panel':
                nested = element.get('elements', [])
                self._load_elements(nested, parent=element_obj)
            elif element['type'] == 'paneldynamic':
                nested = element.get('templateElements', element.get('elements', []))
                self._load_elements(nested, parent=element_obj)

    def get_element_class(self, element):
        """Dynamically load the element class based on the element type."""
        element_type = element.get('type')
        element_type_cap = element_type.capitalize() if element_type else None
        if not element_type:
            return None

        cls_mapping = self.element_class_mapping.get(element_type)
        if cls_mapping:
            cls_mapping = cls_mapping.capitalize() if isinstance(cls_mapping, str) else cls_mapping
            if isinstance(cls_mapping, str):
                cls_name = cls_mapping
                import_path = f"surveyjs.elements.{element_type}.{cls_mapping}"
                try:
                    module = __import__(import_path, fromlist=[cls_name])
                    cls = getattr(module, cls_name)
                    return cls
                except (AttributeError, ModuleNotFoundError) as e:
                    logger.warning(
                        "Could not load element class for type '%s': %s. "
                        "Falling back to base Question Element.", element_type, e
                    )
                    return Element
            else:
                return cls_mapping
        else:
            cls_name = f"Question{element_type_cap}"
            import_path = 'surveyjs.elements.%s' % element_type
            try:
                module = __import__(import_path, fromlist=[cls_name])
                return getattr(module, cls_name)
            except (AttributeError, ModuleNotFoundError) as e:
                logger.warning(
                    "Could not load question class for type '%s': %s. "
                    "Falling back to base Question Element.", element_type, e
                )
                return Element

    def get_element_object(self, element):
        """Create a element object from an element dict."""
        cls = self.get_element_class(element)
        if cls is None:
            return None
        return cls(element, self, language=self.language, i18n=self.i18n)

    @property
    def form(self):
        """Placeholder form dict (always empty). Useful in contexts where
        a element owner's form is requested."""
        return {}
