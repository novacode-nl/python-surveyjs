# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from collections import OrderedDict

from .text import translate_text


class Page:
    """
    Represents a single page of a SurveyJS survey.

    Pages group root elements into sections. They are *not* survey elements
    themselves, so they never appear in an owner's `all_elements`,
    `questions` or `all_element_paths` registries — they are reached through
    `SurveyCreator.pages` / `SurveyForm.pages` only.

    Schemas without a `pages` key (a flat top-level `elements` array) are
    represented by a single implicit page, so consumers always have one code
    path.
    """

    def __init__(self, raw, owner, index=0, language='default', i18n=None, implicit=False):
        """
        @param raw: The raw JSON page dict from the survey schema
        @param owner: The SurveyCreator or SurveyForm that owns this page
        @param index: Zero-based position of the page in the survey
        @param implicit: True when synthesised for a pages-less schema
        """
        self.raw = raw
        self.owner = owner
        self.index = index
        self.language = language
        self.i18n = i18n or {}
        self.implicit = implicit

        # Root elements on this page, keyed by name. Nested children are
        # reached via each container's `elements`.
        self._elements = OrderedDict()

    # --- Properties ---

    @property
    def elements(self):
        return self._elements

    @property
    def questions(self):
        """Root questions (inputs) on this page, keyed by name."""
        return OrderedDict(
            (name, el) for name, el in self._elements.items() if el.is_question
        )

    @property
    def name(self):
        """The unique name of the page.

        SurveyJS omits `name` on generated pages; fall back to its
        positional name (`page1`, `page2`, ...) as SurveyJS itself does.
        """
        return self.raw.get('name') or 'page%d' % (self.index + 1)

    @property
    def title(self):
        """The display title of the page (falls back to its name)."""
        return self.translate(self.raw.get('title')) or self.translate(self.name)

    @property
    def description(self):
        """The page description/help text."""
        return self.translate(self.raw.get('description', ''))

    def translate(self, text):
        """`text` in this page's language; see `surveyjs.text.translate_text`."""
        return translate_text(text, self.language, self.i18n)

    @property
    def is_visible(self):
        """Whether the page is visible."""
        return self.raw.get('visible', True)

    @property
    def visible_if(self):
        """The visibleIf expression."""
        return self.raw.get('visibleIf', '')

    @property
    def read_only(self):
        """Whether the page is read-only."""
        return self.raw.get('readOnly', False)

    # --- Element registration ---

    def add_element(self, element):
        """Register a root element onto this page and back-link it."""
        self._elements[element.name] = element
        element.page = self

    # --- Representation ---

    def __repr__(self):
        return '<%s name=%s>' % (self.__class__.__name__, self.name)

    def to_dict(self):
        """Return a dictionary representation of the page."""
        return {
            'name': self.name,
            'title': self.title,
            'elements': [el.to_dict() for el in self._elements.values()],
        }
