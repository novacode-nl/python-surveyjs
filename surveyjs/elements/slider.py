# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

from .question import Question


class QuestionSlider(Question):
    """SurveyJS Slider question.

    Lets a respondent pick a value (or a range) on a numeric scale.

    Value shape depends on ``slider_type``:
    - 'single' (default): a single number, e.g. ``50``
    - 'range': a list of two numbers, e.g. ``[20, 80]``
    """

    @property
    def slider_type(self):
        """'single' or 'range'."""
        return self.raw.get('sliderType', 'single')

    @property
    def is_range(self):
        """Whether this is a range slider (two thumbs)."""
        return self.slider_type == 'range'

    @property
    def min(self):
        return self.raw.get('min', 0)

    @property
    def max(self):
        return self.raw.get('max', 100)

    @property
    def step(self):
        return self.raw.get('step', 1)

    @property
    def show_labels(self):
        return self.raw.get('showLabels', True)

    @property
    def custom_labels(self):
        return self.raw.get('customLabels', [])

    @property
    def label_count(self):
        return self.raw.get('labelCount', -1)

    @property
    def tooltip_visibility(self):
        """'auto', 'always' or 'never'."""
        return self.raw.get('tooltipVisibility', 'auto')

    @property
    def allow_clear(self):
        return self.raw.get('allowClear', False)

    @property
    def allow_swap(self):
        """Range-only: whether thumbs may cross each other."""
        return self.raw.get('allowSwap', True)

    @property
    def min_range_length(self):
        """Range-only: minimum gap between thumbs."""
        return self.raw.get('minRangeLength')

    @property
    def max_range_length(self):
        """Range-only: maximum gap between thumbs."""
        return self.raw.get('maxRangeLength')

    @staticmethod
    def _coerce_number(val):
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return val
        try:
            if '.' in str(val):
                return float(val)
            return int(val)
        except (ValueError, TypeError):
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

    def to_number(self):
        """Return the value as a number (single mode).

        In range mode this returns the lower bound."""
        val = self.value
        if isinstance(val, (list, tuple)):
            return self._coerce_number(val[0]) if val else None
        return self._coerce_number(val)

    def to_range(self):
        """Return the value as a ``[low, high]`` list of numbers.

        In single mode the value is wrapped as ``[value, value]``."""
        val = self.value
        if val is None:
            return None
        if isinstance(val, (list, tuple)):
            return [self._coerce_number(v) for v in val]
        num = self._coerce_number(val)
        return [num, num]
