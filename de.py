# !/usr/bin/python3
# -*- coding: utf-8 -*-

from wte import Word, KEYS, WORD_TYPES
from wte import WORD_TYPES as wt
from wikoo import Li, Template, Section, Link, String
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found
from helpers import merge_two_dicts, check_flag
import miners
from miners import \
    if_any, \
    has_flag_in_name, has_flag_in_explaination, has_flag_in_text, \
    has_section, has_template, has_template_with_flag, \
    has_arg, has_flag, has_value, has_arg_and_value_contain, has_arg_with_flag_in_name, \
    has_flag_in_text_recursive, \
    find_terms, \
    get_label_type, find_explainations, \
    term0_cb, term1_cb, lang0_term1_cb, lang0_term2_cb, t_plus_cb, w_cb, alter_cb, en_conj_cb, \
    find_all, find_any, \
    in_section, in_template, in_arg, in_arg_with_flag_in_value, in_link, in_t_plus, in_callback


LANGUAGES = [ "de", "deutsch", "interlingua" ]
LANG_SECTIONS = [ "deutsch", "-de-", "de" ] # "translingual"
TYPE_OF_SPEECH = {
    wt.NOUN          : ['substantiv', 'demonstrativpronomen', 'vorname', 'inhaltsverzeichnis'],
    wt.ADJECTIVE     : ['adjektiv', 'adjektiv ', 'komparativ'],
    wt.VERB          : ['hilfsverb', 'verb', 'wortverbindung', 'konjugierte form', 'deklinierte form'],
    wt.ADVERB        : ['adverb', 'interrogativadverb', 'kausaladverb', 'konjunktionaladverb', 'lokaladverb', 'modaladverb', 'pronominaladverb', 'temporaladverb'],
    wt.PREDICATIVE   : [],
    wt.CONJUNCTION   : ['konjunktion', 'konjunktionaladverb'],
    wt.PREPOSITION   : ['präposition'],
    wt.PRONOUN       : ['demonstrativpronomen', 'indefinitpronomen', 'interrogativpronomen', 'personalpronomen', 'personalpronomen ', 'possessivpronomen', 'pronomen', 'pronominaladverb', 'reflexives personalpronomen', 'reflexivpronomen', 'relativpronomen', 'reziprokpronomen'],
    wt.INTERJECTION  : ['interjektion'],
    wt.PARTICLE      : ['antwortpartikel', 'fokuspartikel', 'gradpartikel', 'modalpartikel', 'negationspartikel', 'partikel', 'vergleichspartikel', 'partizip ii'],
    wt.ARTICLE       : ['artikel'],
    wt.NUMERAL       : ['numerale'],
    wt.ABBREV        : ['abbrev'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name if t.arg(0) and t.arg(0).lower().strip() in LANGUAGES else None for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'sprache' : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)),
    'wortart' : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'männliche wortformen': lambda t: t.name,
    'weibliche wortformen': lambda t: t.name,
    'übersetzungen': lambda t: t.name,
})
SECTION_NAME_TEMPLATES.update({
    s : lambda t: t.name for s in ['abgeleitete_symbole', 'abkürzungen', 'alle_weiteren_formen', 'alternative_schreibweisen', 'anmerkung', 'anmerkung_keilschrift', 'aussprache', 'bedeutungen', 'beispiele', 'bekannte_namensträger', 'ch&li', 'charakteristische_wortkombinationen', 'dmg', 'entlehnungen', 'erbwörter', 'geflügelte_worte', 'gegenwörter', 'grammatische_merkmale', 'hanja', 'herkunft', 'heteronyme', 'holonyme', 'iso_9', 'koseformen', 'kurzformen', 'lesungen', 'männliche_namensvarianten', 'männliche_wortformen', 'nrs', 'namensvarianten', 'nebenformen', 'nicht_mehr_gültige_schreibweisen', 'oberbegriffe', 'redewendungen', 'runen', 'sinnverwandte_redewendungen', 'sinnverwandte_sprichwörter', 'sinnverwandte_wörter', 'sinnverwandte_zeichen', 'sprichwörter', 'strichreihenfolge', 'symbole', 'synonyme', 'teilbegriffe', 'textbaustein', 'umschrift', 'unterbegriffe', 'verballhornung', 'vergrößerungsformen', 'verkleinerungsformen', 'vokalisierung', 'weibliche_namensvarianten', 'weibliche_wortformen', 'wortbildungen', 'wortfamilie', 'wortschatz-niveau', 'worttrennung', 'yivo', 'in_arabischer_schrift', 'in_hebräischer_schrift', 'in_kyrillischer_schrift', 'in_lateinischer_schrift', 'ähnlichkeiten', 'übersetzungen', 'İa', 'grammatische merkmale']
})


def is_lang_template(t):
    pass

#
def is_lang_section(sec):
    if sec.name in LANG_SECTIONS:
        return True


def is_tos_section(sec):
    if sec.name in TOS_SECTIONS:
        return True
    elif has_template(sec.header, [], TYPE_OF_SPEECH):
        pass


def is_expl_section(sec):
    return sec.name in ["bedeutungen"]
    
    
def Type(search_context, excludes, word):
    sec = search_context
    
    for (tos, section_names) in TYPE_OF_SPEECH.items():
        if sec.name in section_names:
            word.Type = tos
            break


def IsMale(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['m', 'männliche namensvarianten', 'männliche wortformen']] ,
        [has_template, 'deutsch substantiv übersicht', [has_arg, 'Genus', [has_value, 'm']]] ,
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ["f", 'weibliche namensvarianten', 'weibliche wortformen']] ,
        [has_template, 'deutsch substantiv übersicht', [has_arg, 'Genus', [has_value, 'f']]] ,
    ):
        word.IsFeminine = True


def IsNeutre(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['n', 'neutr.'] ] ,
    ):
        word.IsNeutre = True


def IsSingle(search_context, excludes, word):
    pass


def IsPlural(search_context, excludes, word):
    pass
    
    
def SingleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'deutsch substantiv übersicht', [in_arg, (None, ['nominativ singular', 'genitiv singular', 'dativ singular', 'akkusativ singular'])]],
    ):
        if lang is None or lang in LANGUAGES:
            word.SingleVariant = term
            break
        

def PluralVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'deutsch substantiv übersicht', [in_arg, (None, ['nominativ plural', 'genitiv plural', 'dativ plural', 'akkusativ plural'])]],
    ):
        if lang is None or lang in LANGUAGES:
            word.PluralVariant = term
            break


def MaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, 'männliche wortformen', [in_link]],
    ):
        if lang is None or lang in LANGUAGES:
            word.MaleVariant = term
            break


def FemaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, 'weibliche wortformen', [in_link]],
    ):
        if lang is None or lang in LANGUAGES:
            word.FemaleVariant = term
            break
    

def IsVerbPast(search_context, excludes, word):
    # Grammatische Merkmale
    if if_any(search_context, excludes, 
        [has_section, 'grammatische merkmale', 
            [has_flag_in_text_recursive, ['Präteritum', 'Perfekt', 'Konjunktiv']] ,
        ],
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    # Grammatische Merkmale
    if if_any(search_context, excludes, 
        [has_section, 'grammatische merkmale', 
            [has_flag_in_text_recursive, 'Präsens'] ,
        ],
    ):
        word.IsVerbPast = True
    

def IsVerbFutur(search_context, excludes, word):
    pass
    

def Conjugation(search_context, excludes, word):
    # Deutsch Verb Übersicht
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'deutsch verb übersicht', 
            [in_arg, (None, [
                'präsens_ich', 'präsens_du', 'präsens_er', 'sie', 'es', 'präteritum_ich', 'konjunktiv ii_ich', 'imperativ singular', 'imperativ plural', 'partizip ii', 'hilfsverb'])
            ]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_conjugation( lang, term )
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['synonyme'],
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )
    

def Antonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['gegenwörter'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    pass


def Hyponymy(search_context, excludes, word):
    pass


def Meronymy(search_context, excludes, word):
    pass


def Holonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['holonyme'],
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_holonym( lang, term )

    
def Troponymy(search_context, excludes, word):
    pass


def Otherwise(search_context, excludes, word):
    pass


def AlternativeFormsOther(search_context, excludes, word):
    pass


def RelatedTerms(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['sinnverwandte redewendungen', 'sinnverwandte sprichwörter', 'sinnverwandte wörter', 'sinnverwandte zeichen'], [in_link]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)
    

def Coordinate(search_context, excludes, word):
    pass


def Translation(search_context, excludes, word):
    # {{trad|en|cat}} {{t+|fr|ongle|m}}
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "ü"       , [in_arg, (["lang", 0], 1)]],
        [in_template, "üt"      , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad"    , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad-"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad+"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "t"       , [in_arg, (["lang", 0], 1)]],
        [in_template, "t-simple", [in_arg, (["lang", 0], 1)]],
        [in_template, "t+"      , [in_t_plus]],
    ):
        word.add_translation(lang, term)


def LabelType(search_context, excludes, word):
    word.LabelType = get_label_type(search_context)


def ExplainationRaw(search_context, excludes, word):
    li = search_context
    word.ExplainationRaw = li.get_raw()
    
    
def ExplainationTxt(search_context, excludes, word):
    li = search_context
    word.ExplainationTxt = li.get_text().strip()
    
    
def ExplainationExamplesRaw(search_context, excludes, word):
    li = search_context
    for e in li.find_objects(Li, recursive=True):
        if e.base.endswith(":"):
            word.ExplainationExamplesRaw = e.get_raw()
            break
    
def ExplainationExamplesTxt(search_context, excludes, word):
    li = search_context
    for e in li.find_objects(Li, recursive=True):
        if e.base.endswith(":"):
            word.ExplainationExamplesTxt = e.get_text().strip()
            break
