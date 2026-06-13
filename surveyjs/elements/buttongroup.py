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
            if isinstance(choice, dict):
                result.append({
                    'value': choice.get('value'),
                    'text': choice.get('text', str(choice.get('value', ''))),
                    'icon_name': choice.get('iconName'),
                    'icon_size': choice.get('iconSize', 24),
                    'show_caption': choice.get('showCaption', True),
                })
            else:
                result.append({
                    'value': choice,
                    'text': str(choice),
                    'icon_name': None,
                    'icon_size': 24,
                    'show_caption': True,
                })
        return result

    @property
    def allow_clear(self):
        """Whether the clear (deselect) button is shown."""
        return self.raw.get('allowClear', True)
