# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from ..valuespec import NONE_VALUE, OTHER_VALUE
from .element import Element

# TODO
# Move some properties from Element to Question, like is_required, validators, etc.,
# so we can have common question properties (is_required, validators, etc.) in one place.


class Question(Element):
    """
    Base class for all SurveyJS Question types.
    """

    @property
    def is_question(self):
        """Whether this is a question (has user-submitted values).
        Layout elements (panel, html, image) override this to return False."""
        return True

    @property
    def is_input(self):
        """Whether this is a question (has user-submitted values).
        Layout elements (panel, html, image) override this to return False."""
        return self.is_question

    def _choices_spec(self, multiple=False):
        """The value spec of a question that picks from its `choices`: one
        choice value, or a list of them when `multiple`.

        Reads the schema rather than a `choices` property, which not every
        choice question defines. The "Other" and "None" items add their
        values. A question with `choicesByUrl` loads its choices from a URL,
        so its allowed values are unknown here."""
        choices_by_url = self.raw.get('choicesByUrl')
        if choices_by_url:
            item = {'x-choicesByUrl': choices_by_url}
        else:
            values = [
                choice['value']
                for choice in map(self.choice_item, self.raw.get('choices', []))
                if choice['value'] is not None
            ]
            if self.raw.get('showOtherItem', self.raw.get('hasOther', False)):
                values.append(OTHER_VALUE)
            if self.raw.get('showNoneItem', self.raw.get('hasNone', False)):
                values.append(NONE_VALUE)
            item = {'enum': values}
        return {'type': 'array', 'items': item} if multiple else item
