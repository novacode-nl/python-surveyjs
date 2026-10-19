# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionRanking(Question):
    """SurveyJS Ranking question.

    Value is a list of choices in the user's ranked order.
    """

    @property
    def choices(self):
        return self.raw.get('choices', [])

    @property
    def choices_values(self):
        return [self.choice_item(choice) for choice in self.choices]

    @property
    def long_tap(self):
        return self.raw.get('longTap', True)

    @property
    def select_to_rank_enabled(self):
        return self.raw.get('selectToRankEnabled', False)

    def value_spec(self):
        """The choice values, in ranked order."""
        return self._choices_spec(multiple=True)
