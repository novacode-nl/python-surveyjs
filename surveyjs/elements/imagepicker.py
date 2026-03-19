# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionImagepicker(Question):
    """SurveyJS Image Picker question.

    Value is the selected image's value, or a list for multi-select.
    """

    @property
    def choices(self):
        return self.raw.get('choices', [])

    @property
    def multi_select(self):
        return self.raw.get('multiSelect', False)

    @property
    def show_label(self):
        return self.raw.get('showLabel', False)

    @property
    def image_fit(self):
        return self.raw.get('imageFit', 'contain')

    @property
    def image_height(self):
        return self.raw.get('imageHeight', 150)

    @property
    def image_width(self):
        return self.raw.get('imageWidth', 200)

    @property
    def content_mode(self):
        """'image' or 'video'."""
        return self.raw.get('contentMode', 'image')
