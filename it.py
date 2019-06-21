# !/usr/bin/python3
# -*- coding: utf-8 -*-

from wte import KEYS, WORD_TYPES
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


LANGUAGES = [ "it", "italian" ]
LANG_SECTIONS = [ "italian", "-it-", "it" ] # "translingual"
TYPE_OF_SPEECH = {
    wt.NOUN          : ['-nome form-', '-nome-', 'sostantivo', 'sostantivo possessivo', '-sost  form-', '-sost form-', '-sost-'],
    wt.ADJECTIVE     : ['aggettivo', '-agg-', '-agg  form-', '-agg dim-', '-agg form-', '-agg nom-', '-agg num form-', '-agg num-', '-agg poss-', '-loc agg-'],
    wt.VERB          : ['verbo', '-verb  form-', '-verb -', '-verb fm del verbo "[[essere]]", attraverso il {{scn', '-verb form-', '-verb formr-', '-verb-', '-loc verb-'],
    wt.ADVERB        : ['avverbio', '-avv-', '-loc avv-'],
    wt.PREDICATIVE   : [],
    wt.CONJUNCTION   : ['-cong-', '-cong-kk-i-'],
    wt.PREPOSITION   : ['-prep-'],
    wt.PRONOUN       : ['-pronome-', '-pron dim-', '-pron form-', '-pron poss-'],
    wt.INTERJECTION  : ['-inter-'],
    wt.PARTICLE      : ['-part-'],
    wt.ARTICLE       : ['-art-'],
    wt.NUMERAL       : ['-cifr-'],
    wt.ABBREV        : ['-abbr-'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name if t.arg(0) and t.arg(0).lower().strip() in LANGUAGES else None for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'langue'  : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)),
    '-it-'    : lambda t: "-it-",
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
    pass
    
    
def Type(search_context, excludes, word):
    sec = search_context
    
    for (tos, section_names) in TYPE_OF_SPEECH.items():
        if sec.name in section_names:
            word.Type = tos
            break


def IsMale(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "''m pl''"] ,
        [has_flag_in_text, "''m sing''"] ,
        [has_flag_in_text, "''m inv''"] ,
        [in_section, '-verb form-', [has_flag_in_text, "maschile"]],
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "''f pl''"] ,
        [has_flag_in_text, "''f sing''"] ,
        [has_flag_in_text, "''f inv''"] ,
    ):
        word.IsMale = True


def IsNeutre(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['n', 'neutr.'] ] ,
    ):
        word.IsNeutre = True


def IsSingle(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "''m sing''"] ,
        [has_flag_in_text, "''f sing''"] ,
        [has_flag_in_text, "singolare"] ,
    ):
        word.IsSingle = True


def IsPlural(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "''m pl''"] ,
        [has_flag_in_text, "''f pl''"] ,
    ):
        word.IsPlural = True
    
    
def SingleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'tabs', [in_arg, (None, 0)]],
    ):
        if lang is None or lang in LANGUAGES:
            word.SingleVariant = term
            break
        

def PluralVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'tabs', [in_arg, (None, 1)]],
    ):
        if lang is None or lang in LANGUAGES:
            word.PluralVariant = term
            break


def MaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'tabs', [in_arg, (None, 0)]],
    ):
        if lang is None or lang in LANGUAGES:
            word.MaleVariant = term
            break


def FemaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'tabs', [in_arg, (None, 2)]],
    ):
        if lang is None or lang in LANGUAGES:
            word.FemaleVariant = term
            break
    

def IsVerbPast(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "passato"] ,
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "presente"] ,
    ):
        word.IsVerbPresent = True
    

def IsVerbFutur(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "futuro"] ,
    ):
        word.IsVerbFutur = True    
    

def Conjugation(search_context, excludes, word):
    pass
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-sin-'],
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )
    

def Antonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-ant-'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-iperon-', '-hyph-'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hypernym( lang, term )


def Hyponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-ipon-'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hyponym( lang, term )


def Meronymy(search_context, excludes, word):
    pass


def Holonymy(search_context, excludes, word):
    pass

    
def Troponymy(search_context, excludes, word):
    pass


def Otherwise(search_context, excludes, word):
    pass


def AlternativeFormsOther(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-alter-'],
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_alternative_form( lang, term )    


def RelatedTerms(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, '-rel-', [in_link]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)
    

def Coordinate(search_context, excludes, word):
    pass


def Translation(search_context, excludes, word):
    # {{trad|en|cat}} {{t+|fr|ongle|m}}
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "trad"    , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad-"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad+"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "t"       , [in_arg, (["lang", 0], 1)]],
        [in_template, "t-simple", [in_arg, (["lang", 0], 1)]],
        [in_template, "t+"      , [in_t_plus]],
    ):
        word.add_translation(lang, term)

    # Translations
    for section in search_context.find_objects(Section, recursive=False, exclude=excludes):
        if section.name in ['-trad-', '-trad1-', '-trad2-']:
            for li in section.find_objects(Li, recursive=False):
                for t in li.find_objects(Template, recursive=False):
                    lang = t.name
                    for link in li.find_objects(Link, recursive=False):
                        term = link.get_text()
                        word.add_translation(lang, term)
                    break


def LabelType(search_context, excludes, word):
    word.LabelType = get_label_type(search_context, word)


def ExplainationRaw(search_context, excludes, word):
    li = search_context
    word.ExplainationRaw = li.get_raw()
    
    
def ExplainationTxt(search_context, excludes, word):
    li = search_context
    text =  "".join( c.get_text() for c in li.childs if not isinstance(c, (Li, Template)) )
    word.ExplainationTxt = text.strip()
    
    
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
