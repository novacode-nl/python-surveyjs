# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from collections import OrderedDict

from ..text import interpolate_text
from .inputtype import parse_input_value

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
        self._page = None

        # Position of this element within its repeating container (a
        # paneldynamic panel instance), or None outside one. Set on the
        # children a SurveyForm materialises per row of submission data.
        self._panel_index = None

        # The `PanelInstance` this element is a direct child of, or None.
        # A row child's `parent` is the paneldynamic, whose `elements` holds
        # the *template* children and not this row's, so the instance is what
        # actually holds its siblings.
        self._panel_instance = None

        # Child elements (for panels and other containers)
        self._elements = OrderedDict()

        # Submission data at this level
        self.form = {}
        self._all_data = {}

        # i18n
        self.language = kwargs.get('language', 'en')
        self.i18n = kwargs.get('i18n', {})

        self.default_value = self.raw.get('defaultValue')

    def load(self, element_owner, parent=None, data=None, is_form=False,
             register_with_owner=True, register_with_parent=True):
        """Load the element into its owner (Survey or Form) and populate
        data from form submission if applicable.

        The two `register_*` flags exist for elements inside a repeating
        container. A paneldynamic's panel instances all reuse the template's
        names, so those children must not be filed under their name in the
        owner's `questions` map (which row would `questions['year']` be?) nor
        in their parent's `elements` map. They are reached through
        `paneldynamic.panels` and by path instead."""
        self.set_element_owner(element_owner, register=register_with_owner)

        if parent:
            self.set_parent(parent, register=register_with_parent)

        self._all_data = data or {}
        self.load_data(data, is_form=is_form)

    def load_data(self, data, is_form=False):
        """Load value from form submission data."""
        if self.is_question and data:
            try:
                self.raw_value = data[self.name]
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
    def nests_data(self):
        """Whether this element introduces a nesting level in the submission
        data. Containers that merely group elements visually (panel) do not:
        their children's values live at the container's own level. Only
        `paneldynamic` overrides this to True."""
        return False

    @property
    def path(self):
        """Structural path from the survey root to this element, as a list of
        names — e.g. ['contactPanel', 'phone'].

        Unlike `name`, this is unique across the whole survey: two
        paneldynamics may each hold a template child named 'year', but their
        paths ('jobs.year' and 'school.year') differ. Stable across parses.

        Inside a materialised panel instance the repeating container carries
        its row index, so a SurveyForm's instance children read
        'education[0].year' where the SurveyCreator's template child reads
        'education.year'."""
        if self._parent is None:
            return [self.name]

        segments = list(self._parent.path)
        if self._panel_index is not None:
            segments[-1] = '%s[%d]' % (segments[-1], self._panel_index)
        return segments + [self.name]

    @property
    def path_str(self):
        """`path` as a dotted string — e.g. 'contactPanel.phone'."""
        return '.'.join(self.path)

    @property
    def _data_prefix(self):
        """Ancestor segments that nest submission data. A nesting container
        contributes its name, followed by this element's row index when the
        element is a materialised panel instance child."""
        if self._parent is None:
            return []
        prefix = list(self._parent._data_prefix)
        if self._parent.nests_data:
            prefix.append(self._parent.name)
            if self._panel_index is not None:
                prefix.append(self._panel_index)
        return prefix

    @property
    def input_path(self):
        """Path to this element's value within the submission data: a list of
        str keys and int row indices, directly usable to index the data.

        - ['phone'] — inside a panel, which is transparent to the data
        - ['education', 'year'] — a Creator *template* child (no row exists)
        - ['education', 0, 'year'] — a Form *instance* child, so that
          `data['education'][0]['year']` is its value

        Only meaningful for questions; layout elements hold no value."""
        return self._data_prefix + [self.name]

    @property
    def input_path_str(self):
        """`input_path` rendered as a string — e.g. 'education[0].year'."""
        rendered = ''
        for segment in self.input_path:
            if isinstance(segment, int):
                rendered += '[%d]' % segment
            else:
                rendered += ('.' if rendered else '') + segment
        return rendered

    def get_value_from(self, data):
        """Resolve this element's value out of a raw submission dict by
        walking its `input_path`."""
        for segment in self.input_path:
            if data is None:
                return None
            try:
                data = data[segment]
            except (KeyError, IndexError, TypeError):
                return None
        return data

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
        """The display title of the element, with text piping applied."""
        title = self.raw.get('title')
        if isinstance(title, dict):
            title = title.get(self.language) or title.get(next(iter(title), None)) or self.name
        if not title:
            title = self.name
        if self.i18n.get(self.language):
            title = self.i18n[self.language].get(title, title)
        return self._interpolate(title)

    @property
    def label(self):
        """Alias for title."""
        return self.title

    @property
    def description(self):
        """The element description/help text, with text piping applied."""
        return self._interpolate(self.raw.get('description', ''))

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
        followers with start_with_new_line False.

        Siblings come from whichever container actually holds them: the
        `PanelInstance` for a materialised paneldynamic row child (its parent
        is the paneldynamic, which holds the template children instead), else
        the element's parent for a nested element, else the element owner for
        a top-level one."""
        if self._panel_instance is not None:
            container = self._panel_instance
        elif self._parent is not None:
            container = self._parent
        else:
            container = self._element_owner
        # `PanelInstance` defines `__len__`, so an empty one is falsy — test
        # for absence explicitly rather than truthiness.
        if container is None:
            return []

        owner_els = list(container.elements.values())

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
        self.set_parent(parent)

    def set_parent(self, parent, register=True):
        """Link this element to its container.

        `register=False` links without filing the element under its name in
        the parent's `elements` map — used for panel instance children, whose
        names repeat across rows."""
        if parent:
            self._parent = parent
            if register:
                self._parent.elements[self.name] = self

    @property
    def panel_index(self):
        """Index of the panel instance this element belongs to, or None if it
        is not inside a repeating container."""
        return self._panel_index

    @panel_index.setter
    def panel_index(self, index):
        self._panel_index = index

    @property
    def _effective_panel_index(self):
        """This element's row index within its dynamic panel, or None.

        Only a direct row child carries the index; an element nested deeper
        (e.g. inside a panel inside a row) inherits it from its container."""
        if self._panel_index is not None:
            return self._panel_index
        if self._parent is not None:
            return self._parent._effective_panel_index
        return None

    def _interpolate(self, text):
        """Apply SurveyJS text piping to `text` for this element's row."""
        return interpolate_text(text, self._effective_panel_index)

    @property
    def panel_instance(self):
        """The `PanelInstance` this element is a direct child of, or None.

        A row child's siblings live here rather than on its `parent`, which is
        the paneldynamic and holds the template children."""
        return self._panel_instance

    @panel_instance.setter
    def panel_instance(self, instance):
        self._panel_instance = instance

    @property
    def in_repeating_context(self):
        """Whether this element lives inside a materialised panel instance.

        Such elements share their name with their counterparts in every other
        row, so they are addressable only by path, never by name."""
        if self._panel_index is not None:
            return True
        if self._parent is not None:
            return self._parent.in_repeating_context
        return False

    @property
    def registrable_children(self):
        """Child elements an owner should walk when building its registries.

        Containers whose children live somewhere other than `elements` (a
        paneldynamic's panel instances) override this."""
        return list(self._elements.values())

    @property
    def page(self):
        """The Page this element belongs to.

        Only root elements are assigned a page directly; nested elements
        (panel/paneldynamic children) inherit their container's page."""
        if self._page is not None:
            return self._page
        if self._parent is not None:
            return self._parent.page
        return None

    @page.setter
    def page(self, page):
        self._page = page

    @property
    def element_owner(self):
        """The element's owner (Survey or Form)."""
        return self._element_owner

    @element_owner.setter
    def element_owner(self, element_owner):
        self.set_element_owner(element_owner)

    def set_element_owner(self, element_owner, register=True):
        """Attach this element to its owner (Survey or Form).

        `register=False` attaches without filing the element under its name in
        the owner's `questions` map — used for panel instance children, whose
        names repeat across rows."""
        self._element_owner = element_owner
        if register and self.is_question:
            self._element_owner.questions[self.name] = self

    # --- Value ---
    #
    # There is one stored value: `raw_value`, exactly as it appears in the
    # submission JSON. `value` is a read-only view of it, parsed according to
    # this element's `inputType`. An element without an `inputType` — every
    # type but `text` and a `multipletext` item — has no parser, so its
    # `value` is its `raw_value`.
    #
    # `value` is derived, so it is not settable: assign `raw_value` instead.
    # Otherwise a caller could store a `date` where JSON is promised, and
    # `to_dict()` would stop being serialisable.

    @property
    def raw_value(self):
        """The value exactly as submitted, or the schema's `defaultValue`.

        Always JSON-serialisable, and always the original when `value` is
        None because the submitted text could not be parsed."""
        val = self.form.get('raw_value', self._none_value)
        if val is self._none_value:
            return self.default_value
        return val

    @raw_value.setter
    def raw_value(self, value):
        self.form['raw_value'] = value

    @property
    def value(self):
        """`raw_value` parsed according to this element's `inputType`.

        A date question yields a `date`, a datetime-local a `datetime`, a
        number an int/float. Elements with no `inputType` yield `raw_value`
        unchanged. An unparseable value yields None — check `raw_value` to
        tell a malformed submission from an empty one."""
        return parse_input_value(self.input_type, self.raw_value)

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
        """Return a dictionary representation of the element (question).

        Emits `raw_value` under the `value` key: a parsed `value` may be a
        `date`, which is not JSON-serialisable."""
        return {
            'name': self.name,
            'type': self.type,
            'title': self.title,
            'value': self.raw_value,
        }
