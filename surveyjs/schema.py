# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""The structure of a SurveyJS schema, as far as this package reads it."""

#: The keys that hold child elements: a schema's pages, a page's or a
#: panel's elements, a dynamic panel's template.
ELEMENT_LISTS = ("pages", "elements", "templateElements")

#: The keys this package reads as text.
TEXT_KEYS = ("name", "type")


class SchemaError(ValueError):
    """A schema whose structure cannot be read: ``problems`` lists what
    (see `check_schema`)."""

    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


def check_schema(schema):
    """What in `schema` (a decoded SurveyJS JSON schema) does not fit the
    structure SurveyJS prescribes, as a list of messages, each starting with
    the path of the offending part; empty when it fits.

    Checks what this package and the SurveyJS library both rely on: an
    object, whose pages, elements and template elements are lists of
    objects, with a text ``name`` and ``type`` where they have one. A schema
    being designed passes: an empty one, or an element without a name or
    type. The element types' own properties are left to SurveyJS."""
    if not isinstance(schema, dict):
        return ["schema: not an object (got %s)" % type(schema).__name__]
    problems = []
    _check_container(schema, "", problems)
    return problems


def _check_container(node, path, problems):
    for key in ELEMENT_LISTS:
        if key not in node:
            continue
        children = node[key]
        key_path = "%s.%s" % (path, key) if path else key
        if not isinstance(children, list):
            problems.append("%s: not a list (got %s)" % (key_path, type(children).__name__))
            continue
        for index, child in enumerate(children):
            child_path = "%s[%d]" % (key_path, index)
            if not isinstance(child, dict):
                problems.append("%s: not an object (got %s)" % (child_path, type(child).__name__))
                continue
            for text_key in TEXT_KEYS:
                if text_key in child and not isinstance(child[text_key], str):
                    problems.append("%s.%s: not text (got %s)" % (child_path, text_key, type(child[text_key]).__name__))
            _check_container(child, child_path, problems)
