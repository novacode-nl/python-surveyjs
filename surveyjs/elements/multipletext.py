# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from ..valuespec import input_type_spec
from .inputtype import parse_input_value
from .question import Question


class MultipleTextItem:
    """One text item of a Multiple Textboxes question.

    Items are not survey elements — they have no `type` and never appear in an
    owner's registries — but each carries its own `inputType`, so each parses
    its value independently of its siblings. Like an element, an item exposes
    `raw_value` (as submitted) and `value` (parsed per its `inputType`).
    """

    def __init__(self, raw, question):
        self.raw = raw
        self.question = question

    @property
    def name(self):
        return self.raw.get('name', '')

    @property
    def title(self):
        """The item's display title, falling back to its name."""
        return self.question.translate(self.raw.get('title')) or self.question.translate(self.name)

    @property
    def input_type(self):
        return self.raw.get('inputType', 'text')

    @property
    def is_required(self):
        return self.raw.get('isRequired', False)

    @property
    def placeholder(self):
        return self.question.translate(self.raw.get('placeholder', ''))

    @property
    def raw_value(self):
        """This item's value exactly as submitted."""
        return self.question.get_item_raw_value(self.name)

    @property
    def value(self):
        """`raw_value` parsed according to this item's own `inputType`."""
        return parse_input_value(self.input_type, self.raw_value)

    def __repr__(self):
        return '<MultipleTextItem name=%s input_type=%s>' % (self.name, self.input_type)

    def to_dict(self):
        """Emits `raw_value` under `value`, so the dict stays JSON-serialisable."""
        return {
            'name': self.name,
            'title': self.title,
            'inputType': self.input_type,
            'value': self.raw_value,
        }


class QuestionMultipletext(Question):
    """SurveyJS Multiple Textboxes question.

    `raw_value` is a dict mapping item names to their submitted values.
    Example: {"firstName": "John", "lastName": "Doe"}

    `value` is that dict with each item's value parsed per the item's own
    `inputType`: {"birth": date(2024, 3, 15)} where `raw_value` holds
    {"birth": "2024-03-15"}. A key with no matching item passes through.
    `item_values`, `get_item_value(name)` and an item's own `value` read the
    same parsed values per item.
    """

    def __init__(self, raw, survey, **kwargs):
        super().__init__(raw, survey, **kwargs)
        self._items = [MultipleTextItem(item, self) for item in self.raw.get('items', [])]

    @property
    def items(self):
        """The item definitions, as `MultipleTextItem` objects."""
        return self._items

    @property
    def item_names(self):
        """Get the list of item names."""
        return [item.name for item in self._items]

    @property
    def item_count(self):
        return len(self._items)

    @property
    def col_count(self):
        return self.raw.get('colCount', 1)

    def get_item(self, item_name):
        """Get an item by name, or None."""
        for item in self._items:
            if item.name == item_name:
                return item
        return None

    @property
    def value(self):
        """A parsed copy of `raw_value`: a new dict with the same keys, each
        item's value parsed per its `inputType`. `raw_value` is unchanged.

        Unlike `item_values`, an item nobody answered is absent rather than
        None."""
        val = self.raw_value
        if not isinstance(val, dict):
            return val
        parsed = {}
        for name, item_raw in val.items():
            item = self.get_item(name)
            parsed[name] = item_raw if item is None else item.value
        return parsed

    def get_item_raw_value(self, item_name):
        """Get an item's value exactly as submitted."""
        val = self.raw_value
        if val and isinstance(val, dict):
            return val.get(item_name)
        return None

    def get_item_value(self, item_name):
        """Get an item's value, parsed according to its own `inputType`."""
        item = self.get_item(item_name)
        if item is None:
            return None
        return item.value

    @property
    def item_values(self):
        """Every item's value, parsed per its own `inputType`, keyed by name."""
        return {item.name: item.value for item in self._items}

    @property
    def raw_item_values(self):
        """Every item's value exactly as submitted, keyed by name."""
        return {item.name: item.raw_value for item in self._items}

    def get_item_title(self, item_name):
        """Get the title for a specific item by name."""
        item = self.get_item(item_name)
        if item is None:
            return item_name
        return item.title

    def value_spec(self):
        """An object keyed by item name, each item shaped by its own
        `inputType`."""
        return {
            'type': 'object',
            'properties': {item.name: input_type_spec(item.input_type) for item in self.items},
            'additionalProperties': False,
        }
