# Copyright 2026 Nova Code (https://www.novacode.nl)
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
        result = []
        for choice in self.choices:
            if isinstance(choice, dict):
                result.append({
                    'value': choice.get('value'),
                    'text': choice.get('text', str(choice.get('value', '')))
                })
            else:
                result.append({'value': choice, 'text': str(choice)})
        return result

    @property
    def long_tap(self):
        return self.raw.get('longTap', True)

    @property
    def select_to_rank_enabled(self):
        return self.raw.get('selectToRankEnabled', False)
