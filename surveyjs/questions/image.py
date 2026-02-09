# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionImage(Question):
    """SurveyJS Image question.

    Displays a static image. Not an input element.
    """

    @property
    def is_input(self):
        """Image elements are display-only, not input questions."""
        return False

    @property
    def image_link(self):
        """Get the image URL."""
        return self.raw.get('imageLink', '')

    @property
    def image_fit(self):
        """Image fit: 'contain', 'cover', 'fill', 'none'."""
        return self.raw.get('imageFit', 'contain')

    @property
    def image_height(self):
        return self.raw.get('imageHeight', 150)

    @property
    def image_width(self):
        return self.raw.get('imageWidth', 200)

    @property
    def alt_text(self):
        return self.raw.get('altText', '')

    @property
    def content_mode(self):
        """Content mode: 'image', 'video', 'youtube'."""
        return self.raw.get('contentMode', 'image')
