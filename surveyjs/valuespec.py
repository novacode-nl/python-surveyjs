# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Value specs: what a question accepts as its value, and checking a value
against that.

Parsing (`Element.value`) reads submitted data. A value spec goes the other
way: it says what value a question accepts, for code that *writes* data into
a form, e.g. prefilling it.

A spec is a small subset of JSON Schema, so it is plain JSON and readable by
people and language models alike:

- `type`: 'string', 'number', 'boolean', 'array' or 'object'
- `enum`: the allowed values
- `format`: for a string, the SurveyJS `inputType` it must fit ('date',
  'datetime-local', 'time', 'month', 'week'), or 'data-url'
- `examples`: a sample value, for a format
- `minimum`, `maximum`: for a number
- `items`, `minItems`, `maxItems`: for an array
- `properties`, `additionalProperties`: for an object
- `x-choicesByUrl`: the question loads its choices from a URL, so the allowed
  values are not known from the schema

`{}` accepts any value. `None` (instead of a spec) means the element holds no
value of its own: a panel, an html or image element, an expression.

`check_spec()` checks a value against a spec. Its messages describe a wrong
value by its type, never by its content, so they can be passed on (e.g. to an
AI that wrote the value) without disclosing any data.
"""

from datetime import datetime

from .elements.inputtype import DATETIME_FORMATS, TIME_FORMATS, parse_week

#: format -> (pattern shown in a message, example value)
FORMAT_HINTS = {
    'date': ('YYYY-MM-DD', '2024-03-15'),
    'datetime-local': ('YYYY-MM-DDTHH:MM', '2024-03-15T13:45'),
    'time': ('HH:MM', '13:45'),
    'month': ('YYYY-MM', '2024-03'),
    'week': ('YYYY-Www', '2024-W11'),
    'data-url': ('data:image/...', 'data:image/png;base64,...'),
}

#: SurveyJS stores the "Other" and "None" items under these values.
OTHER_VALUE = 'other'
NONE_VALUE = 'none'


def _fits_formats(value, formats):
    for fmt in formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def _fits_week(value):
    try:
        parse_week(value)
        return True
    except (ValueError, TypeError):
        return False


#: format -> check of a string value. A format absent here is not checked.
FORMAT_CHECKS = {
    'date': lambda v: _fits_formats(v, ('%Y-%m-%d',)),
    'datetime-local': lambda v: _fits_formats(v, DATETIME_FORMATS),
    'time': lambda v: _fits_formats(v, TIME_FORMATS),
    'month': lambda v: _fits_formats(v, ('%Y-%m',)),
    'week': _fits_week,
    'data-url': lambda v: v.startswith('data:image/'),
}


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def input_type_spec(input_type, minimum=None, maximum=None):
    """The value spec of a text input with this SurveyJS `inputType`.

    Shared by a `text` question, a `multipletext` item and a matrix `text`
    column, which all carry an `inputType`."""
    if input_type in ('number', 'range'):
        spec = {'type': 'number'}
        # Only a numeric bound: a schema may carry it as a string.
        if _is_number(minimum):
            spec['minimum'] = minimum
        if _is_number(maximum):
            spec['maximum'] = maximum
        return spec
    spec = {'type': 'string'}
    if input_type in FORMAT_HINTS:
        spec['format'] = input_type
        spec['examples'] = [FORMAT_HINTS[input_type][1]]
    return spec


def data_properties(elements):
    """`{name: value spec}` of the elements holding a value at this data
    level.

    Looks through a plain panel, whose questions store their values at the
    panel's own level; a dynamic panel or a matrix is one value (a list or a
    dict) of its own."""
    properties = {}
    for element in elements:
        spec = element.value_spec()
        if spec is not None:
            properties[element.name] = spec
        elif not element.nests_data:
            properties.update(data_properties(element.elements.values()))
    return properties


def _type_name(value):
    if value is None:
        return 'null'
    return type(value).__name__


def _same(a, b):
    """Equal, and not merely because Python takes True for 1."""
    return a == b and isinstance(a, bool) == isinstance(b, bool)


def _join(path, key):
    if isinstance(key, int):
        return '%s[%d]' % (path, key)
    return '%s.%s' % (path, key) if path else str(key)


def _expected(spec):
    """What `spec` expects, in words."""
    fmt = spec.get('format')
    if fmt in FORMAT_HINTS:
        pattern, example = FORMAT_HINTS[fmt]
        return "a string in the format %s (e.g. '%s')" % (pattern, example)
    return {
        'string': 'a string',
        'number': 'a number',
        'boolean': 'true or false',
        'array': 'a list',
        'object': 'an object (dict)',
    }.get(spec.get('type'), 'a value')


def check_spec(spec, value, path=''):
    """Check `value` against the value spec `spec`.

    Returns a list of messages, each prefixed with the path of the offending
    value (`jobs[0].year: ...`); an empty list when the value fits. None
    always fits: it leaves a question unanswered. A message never contains
    the value itself, only its type.
    """
    prefix = '%s: ' % path if path else ''
    if spec is None:
        return ['%sholds no value' % prefix]
    if value is None:
        return []
    if 'enum' in spec:
        if any(_same(value, allowed) for allowed in spec['enum']):
            return []
        return ['%sexpected one of %s, got a %s that is not one of them' % (
            prefix, spec['enum'], _type_name(value))]

    spec_type = spec.get('type')
    if spec_type == 'string':
        if not isinstance(value, str):
            return ['%sexpected %s, got %s' % (prefix, _expected(spec), _type_name(value))]
        check = FORMAT_CHECKS.get(spec.get('format'))
        if check and not check(value):
            return ['%sexpected %s, got a str that does not fit' % (prefix, _expected(spec))]
        return []
    if spec_type == 'number':
        if not _is_number(value):
            return ['%sexpected a number, got %s' % (prefix, _type_name(value))]
        if 'minimum' in spec and value < spec['minimum']:
            return ['%sexpected a number of at least %s' % (prefix, spec['minimum'])]
        if 'maximum' in spec and value > spec['maximum']:
            return ['%sexpected a number of at most %s' % (prefix, spec['maximum'])]
        return []
    if spec_type == 'boolean':
        if not isinstance(value, bool):
            return ['%sexpected true or false, got %s' % (prefix, _type_name(value))]
        return []
    if spec_type == 'array':
        return _check_array(spec, value, path, prefix)
    if spec_type == 'object':
        return _check_object(spec, value, path, prefix)
    return []


def _check_array(spec, value, path, prefix):
    if not isinstance(value, list):
        return ['%sexpected a list, got %s' % (prefix, _type_name(value))]
    problems = []
    if 'minItems' in spec and len(value) < spec['minItems']:
        problems.append('%sexpected at least %d items, got %d' % (
            prefix, spec['minItems'], len(value)))
    if 'maxItems' in spec and len(value) > spec['maxItems']:
        problems.append('%sexpected at most %d items, got %d' % (
            prefix, spec['maxItems'], len(value)))
    item_spec = spec.get('items', {})
    for index, item in enumerate(value):
        problems.extend(check_spec(item_spec, item, _join(path, index)))
    return problems


def _check_object(spec, value, path, prefix):
    if not isinstance(value, dict):
        return ['%sexpected an object (dict), got %s' % (prefix, _type_name(value))]
    problems = []
    properties = spec.get('properties', {})
    for key, item in value.items():
        if key in properties:
            problems.extend(check_spec(properties[key], item, _join(path, key)))
        elif spec.get('additionalProperties', True) is False:
            problems.append('%sunknown key; expected one of %s' % (
                '%s: ' % _join(path, key), list(properties)))
    return problems
