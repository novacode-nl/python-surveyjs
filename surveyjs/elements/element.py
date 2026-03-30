# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

import uuid
from collections import OrderedDict

# TODO
# 1. Make a Question class that inherits from Element and all questions inherit from that,
# so we can have common question properties (is_required, validators, etc.) in one place.
# 2. Make a Layout class that inherits from Element and all layout classes (panel) inherit from that.

class Element:
    """
    Base class for all SurveyJS element types.

    Holds the raw JSON element data, provides access to common properties
    (name, type, title, etc.) and handles value loading from form data.
    """

    _none_value = None

    def __init__(self, raw, survey, **kwargs):
        """
        @param raw: The raw JSON element dict from the survey schema
        @param survey: The Survey instance that owns this element
        """
        self.raw = raw
        self.survey = survey

        self._parent = None
        self._element_owner = None

        # Child elements (for panels and other containers)
        self._elements = OrderedDict()

        # Path tracking
        self.survey_path = []
        self.survey_input_path = []

        # ID
        self._id = self.raw.get('id', str(uuid.uuid4()))

        # Submission data at this level
        self.form = {}
        self._all_data = {}

        # i18n
        self.language = kwargs.get('language', 'en')
        self.i18n = kwargs.get('i18n', {})

        self.default_value = self.raw.get('defaultValue')

    def load(self, element_owner, parent=None, data=None, is_form=False):
        """Load the element into its owner (Survey or Form) and populate
        data from form submission if applicable."""
        self.element_owner = element_owner

        if parent:
            self.parent = parent

        self._all_data = data or {}
        self.load_data(data, is_form=is_form)

    def load_data(self, data, is_form=False):
        """Load value from form submission data."""
        if self.is_question and data:
            try:
                self.value = data[self.name]
            except KeyError:
                # Use default value if available
                pass

    # --- Properties ---

    @property
    def is_question(self):
        """Whether this is a question (has user-submitted values).
        Layout elements (panel, html, image) override this to return False."""
        return None

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        if isinstance(elements, OrderedDict):
            self._elements = elements
        else:
            self._elements = OrderedDict(elements)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        """The unique name/key of the element."""
        return self.raw.get('name', '')

    @property
    def type(self):
        """The SurveyJS element type."""
        return self.raw.get('type', '')

    @property
    def title(self):
        """The display title of the element."""
        title = self.raw.get('title')
        if isinstance(title, dict):
            title = title.get(self.language) or title.get(next(iter(title), None)) or self.name
        if not title:
            title = self.name
        if self.i18n.get(self.language):
            return self.i18n[self.language].get(title, title)
        return title

    @property
    def label(self):
        """Alias for title."""
        return self.title

    @property
    def description(self):
        """The element description/help text."""
        return self.raw.get('description', '')

    @property
    def is_required(self):
        """Whether the element is required."""
        return self.raw.get('isRequired', False)

    @property
    def is_visible(self):
        """Whether the element is visible."""
        return self.raw.get('visible', True)

    @property
    def visible_if(self):
        """The visibleIf expression."""
        return self.raw.get('visibleIf', '')

    @property
    def enable_if(self):
        """The enableIf expression."""
        return self.raw.get('enableIf', '')

    @property
    def read_only(self):
        """Whether the question is read-only."""
        return self.raw.get('readOnly', False)

    @property
    def validators(self):
        """The list of validators."""
        return self.raw.get('validators', [])

    @property
    def input_type(self):
        """The input type (for text questions)."""
        return self.raw.get('inputType', '')

    @property
    def placeholder(self):
        """The placeholder text."""
        return self.raw.get('placeholder', '')

    @property
    def start_with_new_line(self):
        """Whether the element should start on a new line (for layout purposes).
        Defaults to True if not specified.

        Disable this property if you want to render the current question on the
        same line or row with the previous question or panel."""
        return self.raw.get('startWithNewLine', True)

    @property
    def elements_on_same_line(self):
        """Return all elements on the same visual line as self, or []
        if self is alone on its line.

        A line group starts with an element whose start_with_new_line is
        True (or the very first element) and includes all consecutive
        followers with start_with_new_line False."""
        if not self._element_owner:
            return []

        owner_els = list(self._element_owner.elements.values())

        # Find the start of self's line group (walk back to the nearest
        # element with start_with_new_line True, or index 0).
        self_idx = owner_els.index(self)
        start = self_idx
        while start > 0 and not owner_els[start].start_with_new_line:
            start -= 1

        # Collect the group: start element + all consecutive followers
        # with start_with_new_line False.
        group = [owner_els[start]]
        for el in owner_els[start + 1:]:
            if el.start_with_new_line:
                break
            group.append(el)

        return group if len(group) > 1 else []

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if parent:
            self._parent = parent
            self._parent.elements[self.name] = self

    @property
    def element_owner(self):
        """The element's owner (Survey or Form)."""
        return self._element_owner

    @element_owner.setter
    def element_owner(self, element_owner):
        self._element_owner = element_owner
        if self.is_question:
            self._element_owner.questions[self.name] = self

    # --- Value ---

    @property
    def value(self):
        """Get the question's value from form data."""
        val = self.form.get('value', self._none_value)
        if val is self._none_value:
            return self.default_value
        return val

    @value.setter
    def value(self, value):
        self.form['value'] = value

    @property
    def raw_value(self):
        """Get the raw (unprocessed) value."""
        return self.form.get('raw_value', self.value)

    @raw_value.setter
    def raw_value(self, value):
        self.form['raw_value'] = value

    # -- custom properties ---
    @property
    def custom_properties(self):
        """The list of customProperties.

        Documentation:
        https://surveyjs.io/form-library/documentation/customize-question-types/add-custom-properties-to-a-form

        E.g. property type itemvalues:
        - Customized text inputs for entering value-text pairs
        - Use this type for arrays of objects with the following structure:
          { value: any, text: string }.
          For example, Dropdown, Checkboxes, and Radio Button Group questions use this type for the choices property.
        """
        return self.raw.get('customProperties', [])

    # --- Representation ---

    def __repr__(self):
        return '<%s name=%s>' % (self.__class__.__name__, self.name)

    def to_dict(self):
        """Return a dictionary representation of the element (question)."""
        return {
            'name': self.name,
            'type': self.type,
            'title': self.title,
            'value': self.value,
        }
