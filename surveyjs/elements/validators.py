# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""SurveyJS `validators` — a question's per-answer validation rules.

Each entry in a question's `validators` array is a dict with a `type`
(``numeric``, ``text``, ``answercount``, ``regex`` or ``email``),
type-specific settings, and an optional `text` overriding the error message.
This module turns those rules into messages and is consulted by
``Element.validation_errors`` once the question is known to be non-empty — an
empty answer is the `required` check's concern, and every validator here
passes on empty input, exactly as SurveyJS does.

Register a validator for a `type` SurveyJS gains later, or override a built-in:

    from surveyjs.elements.validators import register_validator

    @register_validator('creditcard')
    def _creditcard(value, rule, element):
        return None if luhn_ok(value) else 'Invalid card number.'

A validator receives the question's parsed `value`, the rule dict and the
`element`, and returns an error message (str) or None when the value passes.
An unknown `type` is skipped. The `expression` validator is intentionally
absent: evaluating a SurveyJS expression needs a runtime this library does not
carry, so its rules are ignored rather than mis-evaluated.
"""

import re

#: SurveyJS default English messages, keyed by its localization string ids.
#: `{0}`, `{1}`, `{2}` are filled positionally by `_format`.
DEFAULT_MESSAGES = {
    'numericError': 'The value should be numeric.',
    'numericMin': "The '{0}' should be at least {1}",
    'numericMax': "The '{0}' should be at most {1}",
    'numericMinMax': "The '{0}' should be at least {1} and at most {2}",
    'textMinLength': 'Please enter at least {0} character(s).',
    'textMaxLength': 'Please enter no more than {0} character(s).',
    'textMinMaxLength': 'Please enter at least {0} and no more than {1} characters.',
    'textNoDigitsAllow': 'Numbers are not allowed.',
    'minSelectError': 'Please select at least {0} option(s).',
    'maxSelectError': 'Please select no more than {0} option(s).',
    'invalidEmail': 'Please enter a valid e-mail address.',
    # SurveyJS has no default text for a regex mismatch (authors set `text`);
    # this stands in when none is given.
    'regexError': 'Entered value does not match the expected pattern.',
}

#: The email pattern SurveyJS itself uses.
EMAIL_RE = re.compile(
    r"^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@"
    r"((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|"
    r"(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
)


def _format(template, *params):
    """Fill `{0}`, `{1}`, … placeholders in `template` positionally."""
    result = template
    for index, param in enumerate(params):
        result = result.replace('{%d}' % index, str(param))
    return result


def _message(rule, element, key, *params):
    """The error message for a failed `rule`.

    A validator's own `text` wins (translation is the author's job); otherwise
    the default template for `key` is translated through the element's i18n map
    — the same lookup `Element.validation_errors` uses for the required
    message — and its placeholders filled with `params`.
    """
    custom = rule.get('text')
    if custom:
        template = custom
    else:
        template = DEFAULT_MESSAGES.get(key, key)
        lang_map = element.i18n.get(element.language) if element.i18n else None
        if lang_map:
            template = lang_map.get(template, template)
    return _format(template, *params)


def _to_number(value):
    """`value` as an int/float, or None if it is not a number.

    Booleans are not numbers (SurveyJS treats a checkbox's True as
    non-numeric), and a blank string is None rather than zero."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        text = str(value).strip()
    except (TypeError, ValueError):
        return None
    if text == '':
        return None
    try:
        return float(text) if ('.' in text or 'e' in text.lower()) else int(text)
    except ValueError:
        return None


def validate_numeric(value, rule, element):
    """`type: "numeric"` — value must be a number within [minValue, maxValue]."""
    num = _to_number(value)
    if num is None:
        return _message(rule, element, 'numericError')

    min_value = rule.get('minValue')
    max_value = rule.get('maxValue')
    below = min_value is not None and num < min_value
    above = max_value is not None and num > max_value
    if not (below or above):
        return None

    name = element.title
    if min_value is not None and max_value is not None:
        return _message(rule, element, 'numericMinMax', name, min_value, max_value)
    if below:
        return _message(rule, element, 'numericMin', name, min_value)
    return _message(rule, element, 'numericMax', name, max_value)


def validate_text(value, rule, element):
    """`type: "text"` — length bounds and an optional no-digits rule."""
    text = value if isinstance(value, str) else str(value)

    if rule.get('allowDigits') is False and any(ch.isdigit() for ch in text):
        return _message(rule, element, 'textNoDigitsAllow')

    min_length = rule.get('minLength') or 0
    max_length = rule.get('maxLength') or 0
    length = len(text)
    too_short = min_length > 0 and length < min_length
    too_long = max_length > 0 and length > max_length
    if not (too_short or too_long):
        return None

    if min_length > 0 and max_length > 0:
        return _message(rule, element, 'textMinMaxLength', min_length, max_length)
    if too_short:
        return _message(rule, element, 'textMinLength', min_length)
    return _message(rule, element, 'textMaxLength', max_length)


def validate_answercount(value, rule, element):
    """`type: "answercount"` — bound the number of selected options.

    Only meaningful for array answers (checkbox, tagbox); anything else
    passes, as does an empty selection (that is the required check's job)."""
    if not isinstance(value, list):
        return None
    count = len(value)
    if count == 0:
        return None

    min_count = rule.get('minCount')
    max_count = rule.get('maxCount')
    if min_count and count < min_count:
        return _message(rule, element, 'minSelectError', min_count)
    if max_count and count > max_count:
        return _message(rule, element, 'maxSelectError', max_count)
    return None


def validate_regex(value, rule, element):
    """`type: "regex"` — every answer value must match `regex`.

    Each element of an array answer is tested; a value that fails to compile
    (an author typo) is treated as no constraint rather than a crash."""
    pattern = rule.get('regex')
    if not pattern:
        return None
    flags = re.IGNORECASE if rule.get('caseInsensitive') else 0
    try:
        compiled = re.compile(pattern, flags)
    except re.error:
        return None

    values = value if isinstance(value, list) else [value]
    for item in values:
        if item in (None, ''):
            continue
        if not compiled.search(str(item)):
            return _message(rule, element, 'regexError')
    return None


def validate_email(value, rule, element):
    """`type: "email"` — value must look like an e-mail address."""
    text = str(value).strip()
    if not text:
        return None
    if not EMAIL_RE.match(text):
        return _message(rule, element, 'invalidEmail')
    return None


#: validator `type` -> function. Types absent here are skipped.
VALIDATORS = {
    'numeric': validate_numeric,
    'text': validate_text,
    'answercount': validate_answercount,
    'regex': validate_regex,
    'email': validate_email,
}


def register_validator(type_name):
    """Register (or replace) the function for a validator `type`.

    Usable as a decorator; see the module docstring."""
    def decorator(fn):
        VALIDATORS[type_name] = fn
        return fn
    return decorator


def run_validators(element):
    """Run every recognised validator on `element`, keyed by validator type.

    @return dict: {validator_type: message} for each failing validator. A
        type with no configured validator, or one that passes, is omitted.
    """
    errors = {}
    value = element.value
    for rule in element.validators:
        if not isinstance(rule, dict):
            continue
        fn = VALIDATORS.get(rule.get('type'))
        if fn is None:
            continue
        message = fn(value, rule, element)
        if message:
            errors[rule.get('type')] = message
    return errors
