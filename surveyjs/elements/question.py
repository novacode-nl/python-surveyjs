# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from ..valuespec import NONE_VALUE, OTHER_VALUE
from .element import Element

#: Suffix of the key SurveyJS stores a question's comment under, next to its
#: value (`settings.commentSuffix`): `{"color": "other",
#: "color-Comment": "Turquoise"}`.
COMMENT_SUFFIX = '-Comment'

#: A choice with its own comment area (`choices[].showCommentArea`) stores the
#: comment inside the value, next to the choice value:
#: `{"reason": {"value": "service", "comment": "Too slow"}}`.
CHOICE_VALUE_FIELD = 'value'
CHOICE_COMMENT_FIELD = 'comment'

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

    def load_data(self, data, is_form=False):
        """Load the value, and the comment stored next to it."""
        super().load_data(data, is_form=is_form)
        if self.is_question and data and self.comment_name in data:
            self.form['comment'] = data[self.comment_name]

    @property
    def comment_name(self):
        """The key of this question's comment in the submission data, next
        to its value (`value_name`)."""
        return self.value_name + COMMENT_SUFFIX

    @property
    def comment(self):
        """The text stored under `comment_name`, or None.

        That is the comment area (`showCommentArea`) or, on a choice question,
        the text typed for its "Other" item, see `other_value`."""
        return self.form.get('comment')

    @property
    def has_other(self):
        """Whether the "Other" item is enabled (choice questions)."""
        return self.raw.get('showOtherItem', self.raw.get('hasOther', False))

    @property
    def other_text(self):
        """The label of the "Other" item."""
        return self.translate(self.raw.get('otherText', 'Other'))

    @property
    def other_value(self):
        """The text the respondent typed for the "Other" item, or None when
        that item was not picked (or there is none, or nothing was typed).

        SurveyJS stores the text under `comment_name`, and 'other' in the
        value. Not when `storeOthersAsComment` is off (on the question or on
        the survey) or a comment area takes that key (`showCommentArea`):
        then the text takes the place of 'other' in the value itself."""
        if not self.has_other:
            return None
        values = self._picked_values()
        if self._stores_other_as_comment():
            return (self.comment or None) if OTHER_VALUE in values else None
        if self.raw.get('choicesByUrl'):
            # Its choices are unknown here, so is which value is the text.
            return None
        known = [choice['value'] for choice in map(self.choice_item, self.raw.get('choices', []))]
        known += [OTHER_VALUE, NONE_VALUE]
        return next((one for one in values if one not in known and one not in (None, '')), None)

    @property
    def choice_comments(self):
        """The comment typed for each picked choice that has its own comment
        area (`choices[].showCommentArea`), keyed by choice value:
        `{'service': 'Too slow'}`. Empty when there are none.

        The "Other" item's text is not in here, see `other_value`."""
        value = self.raw_value
        items = value if isinstance(value, list) else [value]
        comments = {}
        for item in items:
            if isinstance(item, dict) and item.get(CHOICE_COMMENT_FIELD) not in (None, ''):
                comments[item.get(self._choice_value_field)] = item[CHOICE_COMMENT_FIELD]
        return comments

    @property
    def _choice_value_field(self):
        """The key of the choice value in a picked item stored as an object."""
        return CHOICE_VALUE_FIELD

    def _unwrap_choice(self, item):
        """The choice value of one picked item, which SurveyJS stores as an
        object when it carries a choice comment (or, on a checkbox, when it
        has a `valuePropertyName`)."""
        if isinstance(item, dict):
            return item.get(self._choice_value_field)
        return item

    def _picked_values(self):
        """The picked choice values, as a list of plain values."""
        value = self.raw_value
        items = value if isinstance(value, list) else [value]
        return [self._unwrap_choice(item) for item in items]

    def _has_choice_comments(self):
        """Whether a choice other than "Other" has its own comment area."""
        return bool(self._comment_choice_values())

    def _stores_other_as_comment(self):
        """Whether the "Other" text is stored under `comment_name`, as SurveyJS
        decides it (`QuestionSelectBase.getStoreOthersAsComment`)."""
        if self.raw.get('showCommentArea', self.raw.get('hasComment', False)):
            return False
        store = self.raw.get('storeOthersAsComment', 'default')
        if store == 'default':
            schema = getattr(self.survey, 'schema', None) or {}
            store = schema.get('storeOthersAsComment', True)
        return bool(store)

    def _choice_text(self, value, choice_texts):
        """The text of one picked `value`: its choice's text, from
        `choice_texts` (value -> text). For the "Other" item, the text typed
        for it, else the item's label."""
        if value in choice_texts:
            return choice_texts[value]
        if self.has_other and (value == OTHER_VALUE or value == self.other_value):
            return self.other_value or self.other_text
        return str(value)

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
            if self.has_other:
                values.append(OTHER_VALUE)
            if self.raw.get('showNoneItem', self.raw.get('hasNone', False)):
                values.append(NONE_VALUE)
            item = {'enum': values}
        if multiple:
            field = self._item_object_field()
            if field:
                properties = {field: item}
                if self._has_choice_comments():
                    properties[CHOICE_COMMENT_FIELD] = {'type': 'string'}
                item = {'type': 'object', 'properties': properties}
            return {'type': 'array', 'items': item}
        comment_values = self._comment_choice_values()
        if comment_values and 'enum' in item:
            # SurveyJS stores {"value": ..., "comment": ...} once a comment is
            # typed for such a choice, the plain value otherwise.
            return {'anyOf': [item, {'type': 'object', 'properties': {
                CHOICE_VALUE_FIELD: {'enum': comment_values},
                CHOICE_COMMENT_FIELD: {'type': 'string'},
            }, 'additionalProperties': False}]}
        return item

    def _comment_choice_values(self):
        """The values of the choices, other than "Other", with their own
        comment area."""
        return [
            choice.get('value') for choice in self.raw.get('choices', [])
            if isinstance(choice, dict) and choice.get('showCommentArea')
            and choice.get('value') != OTHER_VALUE
        ]

    def _item_object_field(self):
        """The key of the choice value when each picked item of a list is
        stored as an object, else ''. Only a checkbox (and a tagbox) stores
        objects for every item."""
        return ''
