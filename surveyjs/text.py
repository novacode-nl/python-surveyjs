# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""SurveyJS text piping: placeholders substituted into displayed text.

SurveyJS lets an author embed placeholders in a title or description, which it
substitutes when rendering. Only `{panelIndex}` is supported here; other pipes
(`{question}`, `{row.field}`, `{panel.field}`) are left untouched.
"""

PANEL_INDEX = '{panelIndex}'


def interpolate_text(text, panel_index=None):
    """Substitute text-piping placeholders in `text`.

    `{panelIndex}` becomes the **1-based** position of the element's row within
    its dynamic panel, matching SurveyJS. Outside a repeating context there is
    no row number, so the placeholder is left as authored.

    @param text: The authored text, or a falsy value.
    @param panel_index: Zero-based row index, or None outside a dynamic panel.
    """
    if not text or '{' not in text:
        return text
    if panel_index is not None:
        text = text.replace(PANEL_INDEX, str(panel_index + 1))
    return text
