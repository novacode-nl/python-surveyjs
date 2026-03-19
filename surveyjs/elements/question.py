# Copyright 2026 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

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
