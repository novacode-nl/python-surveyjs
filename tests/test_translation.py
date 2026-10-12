# Copyright 2026 Nova Code (https://www.novaforms.io)
# See LICENSE file for full licensing details.

"""Tests for translating displayed text.

Every display text goes through `translate_text`: a SurveyJS localizable
dict (`{"default": "Yes", "fr": "Oui"}`) picks the survey's language, and the
`i18n` map (`{language: {source: translation}}`) translates the result.
"""

import json
import unittest

from surveyjs import SurveyCreator, SurveyForm
from surveyjs.text import translate_text

I18N = {'fr': {
    'Yes': 'Oui', 'No': 'Non', 'Red': 'Rouge', 'Other': 'Autre',
    '{{field}} is required': '{{field}} est obligatoire',
}}

SCHEMA = {'pages': [{'name': 'p1', 'title': {'default': 'Start', 'fr': 'Début'}, 'elements': [
    {'type': 'boolean', 'name': 'agree', 'isRequired': True,
     'title': {'default': 'Agree?', 'fr': 'D’accord ?'},
     'description': {'default': 'Read first', 'fr': 'Lisez d’abord'}},
    {'type': 'boolean', 'name': 'own', 'labelTrue': {'default': 'Sure', 'fr': 'Bien sûr'}},
    {'type': 'dropdown', 'name': 'color', 'choices': [
        'Red', {'value': 'b', 'text': {'default': 'Blue', 'fr': 'Bleu'}}, {'value': 'g'}]},
    {'type': 'buttongroup', 'name': 'size', 'choices': [
        {'value': 's', 'text': {'default': 'Small', 'fr': 'Petit'}, 'iconName': 'icon-s'}]},
    {'type': 'checkbox', 'name': 'colors', 'choices': ['Red', 'Green']},
    {'type': 'matrix', 'name': 'm', 'columns': [{'value': 1, 'text': {'fr': 'Un'}}], 'rows': ['Red']},
    {'type': 'multipletext', 'name': 'mt', 'items': [{'name': 'a', 'title': {'fr': 'Ah'}}]},
    {'type': 'matrixdynamic', 'name': 'md', 'columns': [{'name': 'c', 'title': {'fr': 'Cé'}}]},
    {'type': 'text', 'name': 'mail', 'validators': [
        {'type': 'email', 'text': {'default': 'Bad mail', 'fr': 'Mauvais courriel'}}]},
]}]}


def make_form(data, language='fr'):
    return SurveyForm(data, creator=SurveyCreator(SCHEMA, language=language, i18n=I18N))


class TestTranslateText(unittest.TestCase):

    def test_localizable_dict_picks_language(self):
        self.assertEqual(translate_text({'default': 'Yes', 'fr': 'Oui'}, 'fr'), 'Oui')

    def test_localizable_dict_falls_back_to_default(self):
        self.assertEqual(translate_text({'fr': 'Oui', 'default': 'Yes'}, 'de'), 'Yes')

    def test_localizable_dict_falls_back_to_first(self):
        self.assertEqual(translate_text({'fr': 'Oui'}, 'de'), 'Oui')

    def test_i18n_map(self):
        self.assertEqual(translate_text('Yes', 'fr', I18N), 'Oui')

    def test_i18n_map_after_dict(self):
        self.assertEqual(translate_text({'default': 'Yes'}, 'fr', I18N), 'Oui')

    def test_untranslated_kept(self):
        self.assertEqual(translate_text('Maybe', 'fr', I18N), 'Maybe')
        self.assertEqual(translate_text('Yes', 'de', I18N), 'Yes')

    def test_non_text_unchanged(self):
        self.assertIsNone(translate_text(None, 'fr', I18N))
        self.assertEqual(translate_text(3, 'fr', I18N), 3)


class TestTranslatedForm(unittest.TestCase):

    def setUp(self):
        self.form = make_form({'agree': True, 'own': True, 'color': 'Red',
                               'colors': ['Red', 'Green'], 'mail': 'nope'})
        self.q = self.form.questions

    def test_page_title(self):
        self.assertEqual(self.form.pages[0].title, 'Début')

    def test_title_and_description(self):
        self.assertEqual(self.q['agree'].title, 'D’accord ?')
        self.assertEqual(self.q['agree'].description, 'Lisez d’abord')

    def test_boolean_labels_via_i18n(self):
        self.assertEqual(self.q['agree'].label_true, 'Oui')
        self.assertEqual(self.q['agree'].label_false, 'Non')
        self.assertEqual(self.q['agree'].value_text, 'Oui')

    def test_boolean_labels_localizable(self):
        self.assertEqual(self.q['own'].label_true, 'Bien sûr')
        self.assertEqual(self.q['own'].value_text, 'Bien sûr')

    def test_choices(self):
        self.assertEqual(
            [c['text'] for c in self.q['color'].choices_values], ['Rouge', 'Bleu', 'g'])
        self.assertEqual(self.q['color'].value_text, 'Rouge')
        self.assertEqual(self.q['color'].other_text, 'Autre')

    def test_checkbox_value_texts(self):
        self.assertEqual(self.q['colors'].value_texts, ['Rouge', 'Green'])

    def test_buttongroup_keeps_extras(self):
        item = self.q['size'].choices_values[0]
        self.assertEqual(item['text'], 'Petit')
        self.assertEqual(item['icon_name'], 'icon-s')

    def test_matrix_rows_and_columns(self):
        self.assertEqual(self.q['m'].column_values, [{'value': 1, 'text': 'Un'}])
        self.assertEqual(self.q['m'].row_values, [{'value': 'Red', 'text': 'Rouge'}])

    def test_multipletext_item_and_matrix_column_titles(self):
        self.assertEqual(self.q['mt'].get_item_title('a'), 'Ah')
        self.assertEqual(self.q['md'].get_column('c').title, 'Cé')

    def test_required_message(self):
        form = make_form({})
        self.assertEqual(form.questions['agree'].validation_errors(),
                         {'required': 'D’accord ? est obligatoire'})

    def test_validator_text(self):
        self.assertEqual(self.q['mail'].validation_errors(), {'email': 'Mauvais courriel'})


class TestFormLanguage(unittest.TestCase):

    def test_form_inherits_creator_language(self):
        self.assertEqual(make_form({}).lang, 'fr')

    def test_lang_reaches_a_schema_built_creator(self):
        form = SurveyForm({'own': True}, creator_schema_json=json.dumps(SCHEMA), lang='fr')
        self.assertEqual(form.questions['own'].value_text, 'Bien sûr')
        self.assertEqual(form.pages[0].title, 'Début')


NESTED_SCHEMA = {'elements': [
    {'type': 'boolean', 'name': 'root'},
    {'type': 'panel', 'name': 'box', 'elements': [{'type': 'boolean', 'name': 'inPanel'}]},
    {'type': 'paneldynamic', 'name': 'rows', 'templateElements': [
        {'type': 'boolean', 'name': 'inRow'}]},
    {'type': 'matrixdynamic', 'name': 'grid', 'columns': [{'name': 'cell', 'cellType': 'boolean'}]},
]}

NESTED_DATA = {'root': True, 'inPanel': True, 'rows': [{'inRow': True}], 'grid': [{'cell': False}]}


class TestExplicitFormLang(unittest.TestCase):
    """A form's explicit `lang` wins over its creator's `language`, at every
    level: root questions, panel children, dynamic panel rows, matrix cells."""

    def setUp(self):
        creator = SurveyCreator(NESTED_SCHEMA, language='default', i18n=I18N)
        self.form = SurveyForm(NESTED_DATA, creator=creator, lang='fr')
        self.creator = creator

    def test_root_question(self):
        self.assertEqual(self.form.questions['root'].value_text, 'Oui')

    def test_panel_child(self):
        self.assertEqual(self.form.questions['inPanel'].value_text, 'Oui')

    def test_dynamic_panel_row_child(self):
        self.assertEqual(self.form.questions['rows'].get_panel(0)['inRow'].value_text, 'Oui')

    def test_matrix_cell(self):
        self.assertEqual(self.form.questions['grid'].get_cell(0, 'cell').value_text, 'Non')

    def test_creator_keeps_its_own_language(self):
        self.assertEqual(self.creator.questions['root'].label_true, 'Yes')


# Several nesting levels: panel > paneldynamic > (panel > question, matrix,
# multipletext). Every level builds its children through the creator, so each
# must hand its own language down.
DEEP_I18N = {'fr': {
    'Yes': 'Oui', 'No': 'Non', 'Name': 'Nom', 'Add New': 'Ajouter',
    'Row {panelIndex}': 'Ligne {panelIndex}', 'Bad mail': 'Mauvais courriel',
    '{{field}} is required': '{{field}} est obligatoire',
}}

DEEP_SCHEMA = {'pages': [{'name': 'p', 'title': {'default': 'Start', 'fr': 'Début'}, 'elements': [
    {'type': 'panel', 'name': 'outer', 'elements': [
        {'type': 'paneldynamic', 'name': 'pd', 'templateTitle': 'Row {panelIndex}',
         'templateElements': [
             {'type': 'panel', 'name': 'inner', 'elements': [
                 {'type': 'boolean', 'name': 'deep', 'isRequired': True}]},
             {'type': 'matrixdynamic', 'name': 'mx', 'columns': [
                 {'name': 'c', 'cellType': 'boolean'}]},
             {'type': 'multipletext', 'name': 'mt', 'items': [{'name': 'n', 'title': 'Name'}]},
             {'type': 'text', 'name': 'mail', 'validators': [
                 {'type': 'email', 'text': 'Bad mail'}]},
         ]},
    ]},
]}]}

DEEP_DATA = {'pd': [{'mx': [{'c': True}], 'mail': 'nope'}]}


class DeepCase(unittest.TestCase):
    """Reads the translatable texts of the deep schema at every level."""

    def texts(self, form):
        pd = form.questions['pd']
        row = pd.get_panel(0)
        return {
            'page': form.pages[0].title,
            'deep': form.get_element_by_path('outer.pd[0].inner.deep').label_true,
            'cell': row['mx'].get_cell(0, 'c').value_text,
            'item': row['mt'].get_item_title('n'),
            'row_title': row.title,
            'add': pd.panel_add_text,
        }

    FR = {'page': 'Début', 'deep': 'Oui', 'cell': 'Oui', 'item': 'Nom',
          'row_title': 'Ligne 1', 'add': 'Ajouter'}
    EN = {'page': 'Start', 'deep': 'Yes', 'cell': 'Yes', 'item': 'Name',
          'row_title': 'Row 1', 'add': 'Add New'}

    def creator(self, language):
        return SurveyCreator(DEEP_SCHEMA, language=language, i18n=DEEP_I18N)


class TestDeepCascade(DeepCase):
    """The form's language reaches every nesting level."""

    def test_explicit_lang(self):
        form = SurveyForm(DEEP_DATA, creator=self.creator('default'), lang='fr')
        self.assertEqual(self.texts(form), self.FR)

    def test_inherited_from_creator(self):
        form = SurveyForm(DEEP_DATA, creator=self.creator('fr'))
        self.assertEqual(self.texts(form), self.FR)

    def test_explicit_default_overrides_creator(self):
        """'default' given explicitly is a choice, not an absence."""
        form = SurveyForm(DEEP_DATA, creator=self.creator('fr'), lang='default')
        self.assertEqual(self.texts(form), self.EN)

    def test_schema_json_with_lang(self):
        form = SurveyForm(DEEP_DATA, creator_schema_json=json.dumps(DEEP_SCHEMA), lang='fr')
        self.assertEqual(form.questions['pd'].get_panel(0)['mx'].get_cell(0, 'c').language, 'fr')
        self.assertEqual(form.pages[0].title, 'Début')

    def test_schema_json_without_lang(self):
        form = SurveyForm(DEEP_DATA, creator_schema_json=json.dumps(DEEP_SCHEMA))
        self.assertEqual(form.lang, 'default')
        self.assertEqual(form.pages[0].title, 'Start')

    def test_template_panel(self):
        """The blank row for rendering an empty form follows the form too."""
        form = SurveyForm({}, creator=self.creator('default'), lang='fr')
        blank = form.questions['pd'].template_panel
        self.assertEqual(blank.title, 'Ligne 1')
        self.assertEqual(blank['inner'].elements['deep'].label_true, 'Oui')
        self.assertEqual(blank['mt'].get_item_title('n'), 'Nom')
        self.assertEqual(blank['mx'].language, 'fr')

    def test_language_without_translations_falls_back(self):
        """No i18n entries for 'de': localizable dicts fall back to
        `default`, plain texts stay as authored — at every level."""
        form = SurveyForm(DEEP_DATA, creator=self.creator('fr'), lang='de')
        self.assertEqual(self.texts(form), self.EN)


class TestDeepValidationMessages(DeepCase):

    def setUp(self):
        self.form = SurveyForm(DEEP_DATA, creator=self.creator('default'), lang='fr')

    def test_required_message_nested(self):
        deep = self.form.get_element_by_path('outer.pd[0].inner.deep')
        self.assertEqual(deep.validation_errors(), {'required': 'deep est obligatoire'})

    def test_validator_text_nested(self):
        mail = self.form.questions['pd'].get_panel(0)['mail']
        self.assertEqual(mail.validation_errors(), {'email': 'Mauvais courriel'})


class TestSharedCreator(DeepCase):
    """Forms only read their creator: languages never leak between them."""

    def setUp(self):
        self.creator_obj = self.creator('default')
        self.fr = SurveyForm(DEEP_DATA, creator=self.creator_obj, lang='fr')
        self.en = SurveyForm(DEEP_DATA, creator=self.creator_obj)

    def test_forms_independent(self):
        self.assertEqual(self.texts(self.fr), self.FR)
        self.assertEqual(self.texts(self.en), self.EN)

    def test_creator_keeps_its_language_when_nested(self):
        deep = self.creator_obj.get_element_by_path('outer.pd.inner.deep')
        self.assertEqual(deep.label_true, 'Yes')
        self.assertEqual(self.creator_obj.pages[0].title, 'Start')


class TestDefaultLanguage(unittest.TestCase):

    def test_default_locale(self):
        q = make_form({'own': True}, language='default').questions
        self.assertEqual(q['agree'].title, 'Agree?')
        self.assertEqual(q['own'].value_text, 'Sure')
        self.assertEqual(q['agree'].label_true, 'Yes')


if __name__ == '__main__':
    unittest.main()
