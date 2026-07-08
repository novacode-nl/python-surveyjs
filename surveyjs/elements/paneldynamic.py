# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from collections import OrderedDict

from ..text import interpolate_text
from .question import Question


class PanelInstance:
    """One materialised row of a dynamic panel.

    Holds the child elements built for a single entry of the paneldynamic's
    submission data, with their values already populated.
    """

    def __init__(self, panel, index, elements):
        self.panel = panel
        self.index = index
        self.elements = elements

    @property
    def name(self):
        return '%s[%d]' % (self.panel.name, self.index)

    @property
    def title(self):
        """The paneldynamic's `templateTitle` piped for this row.

        The paneldynamic itself sits outside any row, so it cannot resolve
        `{panelIndex}`; the instance can, from its own index."""
        return interpolate_text(self.panel.template_title, self.index)

    @property
    def data(self):
        """The raw submission dict backing this row."""
        return self.panel.panels_data[self.index]

    def get(self, name):
        """Get a child element of this row by name."""
        return self.elements.get(name)

    def __getitem__(self, name):
        return self.elements[name]

    def __iter__(self):
        return iter(self.elements.values())

    def __len__(self):
        return len(self.elements)

    def __repr__(self):
        return '<PanelInstance name=%s>' % self.name

    def to_dict(self):
        return {
            'name': self.name,
            'index': self.index,
            'elements': [el.to_dict() for el in self.elements.values()],
        }


class QuestionPaneldynamic(Question):
    """SurveyJS Dynamic Panel question.

    Allows users to add/remove groups of questions (panels).
    Value is a list of dicts, each dict representing one panel instance.

    A SurveyCreator holds only the *template* children (under `elements`,
    keyed by name). A SurveyForm additionally materialises one set of child
    elements per row of submission data, reachable through `panels`.

    `template_panel` materialises a blank row from the template, for rendering
    an empty form as one representative repeat.
    """

    def __init__(self, raw, survey, **kwargs):
        super().__init__(raw, survey, **kwargs)
        self._panels = []
        self._template_panel = None

    @property
    def panels(self):
        """The materialised panel instances (SurveyForm only; empty on a
        SurveyCreator, which holds the template rather than any rows)."""
        return self._panels

    @property
    def template_panel(self):
        """A blank `PanelInstance` for the repeating template, as row 1.

        There is no submission row to pipe `{panelIndex}` into a template
        child's title, yet rendering a blank form still wants one
        representative repeat. This materialises the template children at
        index 0 with no data, leaving the children the Creator keeps under
        `elements` untouched — mutating those would change their `path` from
        `passengers.first` to `passengers[0].first`.

        Built once, on first access.
        """
        if self._template_panel is None:
            self._template_panel = self._materialise_panel(0, {}, is_form=False)
        return self._template_panel

    def get_panel(self, index):
        """Get a panel instance by row index, or None."""
        if 0 <= index < len(self._panels):
            return self._panels[index]
        return None

    @property
    def registrable_children(self):
        """A dynamic panel's children live in its panel instances, not in
        `elements` — except on a Creator, where `elements` holds the template."""
        children = super().registrable_children
        for panel in self._panels:
            children.extend(panel.elements.values())
        return children

    def load_data(self, data, is_form=False):
        """Load the panel list value, then materialise one set of child
        elements per row of that value.

        Only on the form path: a Creator has no submission data, so it has no
        rows to materialise — it keeps the template children that
        `SurveyCreator._load_elements` builds for it.
        """
        super().load_data(data, is_form=is_form)

        if not is_form:
            return

        self._panels = [
            self._materialise_panel(index, row if isinstance(row, dict) else {})
            for index, row in enumerate(self.panels_data)
        ]

    def _materialise_panel(self, index, row, is_form=True):
        """Build one `PanelInstance`: a fresh set of the template's children,
        stamped with `index` and populated from `row`."""
        elements = OrderedDict()
        for raw in self.template_elements:
            if 'type' not in raw:
                continue
            element_obj = self.survey.get_element_object(raw)
            if not element_obj:
                continue
            element_obj.panel_index = index
            element_obj.load(
                element_owner=self.element_owner,
                parent=self,
                data=row,
                is_form=is_form,
                # Names repeat across rows: file these by path only.
                register_with_owner=False,
                register_with_parent=False,
            )
            elements[element_obj.name] = element_obj
        instance = PanelInstance(self, index, elements)
        # Back-link each child to its row: `parent` is this paneldynamic,
        # whose `elements` holds the template children, so the instance is
        # what holds a child's actual siblings (e.g. for
        # `elements_on_same_line`).
        for element_obj in elements.values():
            element_obj.panel_instance = instance
        return instance

    @property
    def nests_data(self):
        """A dynamic panel's value is a list of dicts, one per panel instance,
        so its template children's values are nested under its own name."""
        return True

    @property
    def template_elements(self):
        """Template elements that repeat for each panel."""
        return self.raw.get('templateElements', self.raw.get('elements', []))

    @property
    def panel_count(self):
        """Initial panel count."""
        return self.raw.get('panelCount', 1)

    @property
    def min_panel_count(self):
        return self.raw.get('minPanelCount', 0)

    @property
    def max_panel_count(self):
        return self.raw.get('maxPanelCount', None)

    @property
    def panel_add_text(self):
        return self.raw.get('panelAddText', 'Add New')

    @property
    def panel_remove_text(self):
        return self.raw.get('panelRemoveText', 'Remove')

    @property
    def allow_add_panel(self):
        return self.raw.get('allowAddPanel', True)

    @property
    def allow_remove_panel(self):
        return self.raw.get('allowRemovePanel', True)

    @property
    def template_title(self):
        return self.raw.get('templateTitle', '')

    @property
    def panels_data(self):
        """Get the value as a list of dicts (panel instances), as submitted."""
        val = self.raw_value
        if isinstance(val, list):
            return val
        return []

    @property
    def actual_panel_count(self):
        """Number of actual panel instances in the data."""
        return len(self.panels_data)

    def get_panel_value(self, panel_index, field_name):
        """Get a specific field value from a panel instance.

        A shortcut for `get_panel(panel_index)[field_name].value`, mirroring
        `SurveyForm.get_value`. Reads through the element, so it honours
        `defaultValue` — unlike a raw lookup into the submission data.

        Only meaningful on a SurveyForm: a SurveyCreator holds the template
        rather than any rows, so it has no panel instances and returns None.

        Args:
            panel_index: Zero-based index of the panel instance.
            field_name: Name of the field within the panel.

        Returns:
            The value of the field, or None.
        """
        panel = self.get_panel(panel_index)
        if panel is None:
            return None
        element = panel.get(field_name)
        if element is None:
            return None
        return element.value
