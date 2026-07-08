# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Parsers for SurveyJS `inputType` values.

SurveyJS stores every text input's value as a string in the submission JSON,
shaped by the element's `inputType` (an HTML input type). This module turns
those strings into Python objects, and is the single place any element type
consults — a `text` question, a `multipletext` item, or a future element that
grows an `inputType`.

`Element.value` is `Element.raw_value` passed through `parse_input_value`, so
registering a parser here is all it takes to type a new `inputType`.

Register a parser for a type SurveyJS gains later, or override a built-in:

    from surveyjs.elements.inputtype import register_input_type

    register_input_type('duration', lambda v: timedelta(seconds=int(v)))

A parser receives the raw value (never None) and returns the parsed object. It
may raise to signal "unparseable"; `parse_input_value` catches that and
returns None. Input types with no registered parser (text, email, url, tel,
password, color) pass their value through unchanged.
"""

from datetime import date, datetime, time

#: Formats accepted for each temporal input type, most specific first.
DATETIME_FORMATS = ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M')
TIME_FORMATS = ('%H:%M:%S', '%H:%M')


def _strptime(value, formats):
    """Parse `value` with the first format that fits, else raise ValueError."""
    text = str(value)
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError('%r matches none of %r' % (text, formats))


def parse_date(value):
    """`inputType: "date"` — '2024-03-15' -> date(2024, 3, 15)."""
    # datetime is a subclass of date, so it must be narrowed before the
    # isinstance(value, date) check, or a datetime would pass through whole.
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return _strptime(value, ('%Y-%m-%d',)).date()


def parse_datetime(value):
    """`inputType: "datetime-local"` — '2024-03-15T13:45' -> datetime."""
    if isinstance(value, datetime):
        return value
    return _strptime(value, DATETIME_FORMATS)


def parse_time(value):
    """`inputType: "time"` — '13:45' -> time(13, 45)."""
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    return _strptime(value, TIME_FORMATS).time()


def parse_month(value):
    """`inputType: "month"` — '2024-03' -> date(2024, 3, 1).

    HTML month inputs carry no day, so the first of the month is used."""
    if isinstance(value, datetime):
        return value.date().replace(day=1)
    if isinstance(value, date):
        return value.replace(day=1)
    return _strptime(value, ('%Y-%m',)).date()


def parse_week(value):
    """`inputType: "week"` — '2024-W11' -> date(2024, 3, 11), the Monday.

    HTML week inputs carry an ISO week number, not a day."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    year, week = str(value).split('-W')
    return date.fromisocalendar(int(year), int(week), 1)


def parse_number(value):
    """`inputType: "number"` / `"range"` — '42' -> 42, '4.2' -> 4.2."""
    if isinstance(value, bool):
        raise TypeError('bool is not a number')
    if isinstance(value, (int, float)):
        return value
    text = str(value)
    return float(text) if '.' in text else int(text)


#: inputType -> parser. Types absent here pass their value through unchanged.
INPUT_TYPE_PARSERS = {
    'date': parse_date,
    'datetime-local': parse_datetime,
    'time': parse_time,
    'month': parse_month,
    'week': parse_week,
    'number': parse_number,
    'range': parse_number,
}


def register_input_type(input_type, parser):
    """Register (or replace) the parser for an `inputType`."""
    INPUT_TYPE_PARSERS[input_type] = parser


def get_input_type_parser(input_type):
    """The parser for `input_type`, or None if its values pass through."""
    return INPUT_TYPE_PARSERS.get(input_type)


def parse_input_value(input_type, value):
    """Parse `value` according to `input_type`.

    Returns None for a None value or an unparseable one, and the value
    unchanged for an input type with no registered parser.
    """
    if value is None:
        return None
    parser = INPUT_TYPE_PARSERS.get(input_type)
    if parser is None:
        return value
    try:
        return parser(value)
    except (ValueError, TypeError, AttributeError, IndexError, KeyError):
        return None
