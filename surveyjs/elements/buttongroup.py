# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .radiogroup import QuestionRadiogroup


class QuestionButtongroup(QuestionRadiogroup):
    """SurveyJS Button Group question.

    A single-select question (like radiogroup) rendered as a row of
    buttons. The ``value`` is a single choice value. Choices may carry
    item-level icon and caption properties.
    """

    @property
    def choices_values(self):
        """Get normalized choice values as a list of dicts with 'value',
        'text' and the button-specific 'icon_name', 'icon_size' and
        'show_caption' properties."""
        result = []
        for choice in self.choices:
            item = self.choice_item(choice)
            extra = choice if isinstance(choice, dict) else {}
            item.update({
                'icon_name': extra.get('iconName'),
                'icon_size': extra.get('iconSize', 24),
                'show_caption': extra.get('showCaption', True),
            })
            result.append(item)
        return result

    @property
    def allow_clear(self):
        """Whether the clear (deselect) button is shown."""
        return self.raw.get('allowClear', True)
