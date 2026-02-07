# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class signaturepadQuestion(Question):
    """SurveyJS Signature Pad question.

    Value is typically a base64-encoded image string.
    """

    @property
    def signature_width(self):
        return self.raw.get('signatureWidth', 300)

    @property
    def signature_height(self):
        return self.raw.get('signatureHeight', 200)

    @property
    def pen_color(self):
        return self.raw.get('penColor', '#1ab394')

    @property
    def background_color(self):
        return self.raw.get('backgroundColor', '#ffffff')

    @property
    def data_format(self):
        """'png', 'jpeg', or 'svg'."""
        return self.raw.get('dataFormat', 'png')

    @property
    def allow_clear(self):
        return self.raw.get('allowClear', True)

    @property
    def is_base64(self):
        """Check if the value is a base64-encoded string."""
        val = self.value
        if val and isinstance(val, str):
            return val.startswith('data:image/')
        return False
