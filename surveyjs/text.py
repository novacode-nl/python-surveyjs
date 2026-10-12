# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""SurveyJS displayed text: translation, and piping placeholders into it.

SurveyJS lets an author embed placeholders in a title or description, which it
substitutes when rendering. Only `{panelIndex}` is supported here; other pipes
(`{question}`, `{row.field}`, `{panel.field}`) are left untouched.
"""

PANEL_INDEX = '{panelIndex}'


def translate_text(text, language, i18n=None):
    """Translate an authored display text into `language`.

    Two sources, applied in turn:

    - A SurveyJS localizable string: a dict keyed by locale, e.g.
      `{"default": "Yes", "fr": "Oui"}`. Picks `language`, else `default`,
      else the first locale given.
    - The `i18n` map, `{language: {source text: translation}}`, looked up
      with the (picked) text. A text it does not list is kept.

    Anything that is not text (None, a number) is returned unchanged.
    """
    if isinstance(text, dict):
        text = text.get(language) or text.get('default') or next(iter(text.values()), None)
    if isinstance(text, str) and text and i18n:
        lang_map = i18n.get(language)
        if lang_map:
            text = lang_map.get(text, text)
    return text


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
