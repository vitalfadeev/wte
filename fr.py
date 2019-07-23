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
    has_template, has_template_with_flag, \
    has_arg, has_flag, has_value, has_arg_and_value_contain, has_arg_with_flag_in_name, \
    find_terms, \
    get_label_type, find_explainations, \
    term0_cb, term1_cb, lang0_term1_cb, lang0_term2_cb, t_plus_cb, w_cb, alter_cb, en_conj_cb, \
    find_all, find_any, \
    in_section, in_template, in_arg, in_arg_with_flag_in_value, in_link, in_t_plus, in_callback


LANGUAGES = [ "fr", "french", "conv" ]
LANG_SECTIONS = [ "french", "-fr-", "fr", "translingual" ]
TYPE_OF_SPEECH = {
    wt.NOUN          : ['nom', 'nom ', 'nom commun', 'nom de famille', 'nom propre', 'nom scientifique'],
    wt.ADJECTIVE     : ['adjectif', 'adjectif ', 'adjectif démonstratif', 'adjectif exclamatif', 'adjectif indéfini', 'adjectif interrogatif', 'adjectif numéral', 'adjectif possessif', 'adjectif relatif'],
    wt.VERB          : ['proverbe', 'verb', 'verbe', 'verbe ', 'verbes:'],
    wt.ADVERB        : ['adverbe', 'adverbe indéfini', 'adverbe interrogatif', 'adverbe pronominal', 'adverbe relatif'],
    wt.PREDICATIVE   : ['predicative'],
    wt.CONJUNCTION   : ['conjonction', 'conjonction ', 'conjonction de coordination'],
    wt.PREPOSITION   : ['préposition', 'préposition '],
    wt.PRONOUN       : ['pronom', 'pronom ', 'pronom démonstratif', 'pronom indéfini', 'pronom interrogatif', 'pronom personnel', 'pronom personnel ', 'pronom possessif', 'pronom relatif', 'prénom'],
    wt.INTERJECTION  : ['interjection'],
    wt.PARTICLE      : ['particule', 'particule numérale'],
    wt.ARTICLE       : ['article', 'article défini', 'article indéfini', 'article partitif'],
    wt.NUMERAL       : ['adjectif numéral', 'numéral', 'particule numérale'],
    wt.ABBREV        : ['abbrev'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name if t.arg(0) and t.arg(0).lower().strip() in LANGUAGES else None for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'langue'  : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)),
    'fr'      : lambda t: 'fr',
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
    
    
def conj(t, excludes, label, *args):
    """
    groupe=1
        INFINITIF : -er
        INDICATIF
            Présent :-e, -es, -e, -ons, -ez, -ent
            Imparfait : -ais, -ais, -ait, -ions, -iez, -aient
            Futur simple : -erai, -eras, -era, -erons, -erez, -eront
            Passé simple : -ai, -as, -a, -âmes, -âtes, -èrent
        SUBJONCTIF
            Présent : -e, -es, -e, -ions, -iez, -ent
            Imparfait : -asse, -asses, -ât, -assions, -assiez, -assent
        CONDITIONNEL
            Présent : -erais, -erais, -erait, -erions, -eriez, -eraient
        IMPÉRATIF
            Présent : -e, -ons, -ez
        PARTICIPE
            Présent : -ant
            Passé : -é, -és, -ée, ées
    """
    pass


def fr_reg_p(t, excludes, label, miners=None):
    # http://en.wiktionary.org/wiki/Template:en-noun
    head = t.arg("head")
    head = head if head else label
    p1 = t.arg(0)
    p = t.arg('p')
    pp = t.arg('pp')

    if pp:
        yield (None, pp)
    elif pp:
        yield (None, pp)
    elif p1:
        yield (None, head + "s")


def Type(search_context, excludes, word):
    sec = search_context
    
    for (tos, section_names) in TYPE_OF_SPEECH.items():
        if sec.name in section_names:
            word.Type = tos
            break


def IsMale(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ["m", 'mf', 'fm', 'au masculin', 'msing']] ,
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ["f", 'mf', 'fm', 'au féminin', 'fsing']] ,
    ):
        word.IsFeminine = True


def IsNeutre(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "n", 'nsing'] ,
    ):
        word.IsNeutre = True


def IsSingle(search_context, excludes, word):
    # singulier
    # 
    if if_any(search_context, excludes, 
        [has_template, ['singulier', 'au singulier', 'au singulier uniquement', 'singulare tantum', 'généralement singulier', 'singulier', 'msing', 'fsing', 'nsing', 'sp']],
    ):
        word.IsSingle = True


def IsPlural(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['au pluriel', 'sp', 'au pluriel', 'au pluriel uniquement', 'fplur', 'généralement pluriel', 'mplur', 'note-plur+', 'nplur', 'plurale tantum', 'pluriel']],
        
    ):
        word.IsPlural = True
    
    
def SingleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'fr-rég', [in_arg, (None, 's')]],
        [in_template, 'fr-accord-mf', [in_arg, (None, 's')]],
    ):
        word.SingleVariant = term
        break
        

def PluralVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'fr-rég', [fr_reg_p, word.LabelName]],
        [in_template, ['fr-accord-mf', 'fr-accord-ind'], [in_arg, (None, ['p', 0])]],
    ):
        word.PluralVariant = term
        break


def MaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'm', [in_arg, (None, 'équiv')]],
    ):
        word.MaleVariant = term
        break


def FemaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'f', [in_arg, (None, 'équiv')]],
    ):
        word.MaleVariant = term
        break
    

def IsVerbPast(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, 'pp'],
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['présent', 'prés']],
    ):
        word.IsVerbPresent = True
    

def IsVerbFutur(search_context, excludes, word):
    pass
    

def Conjugation(search_context, excludes, word):
    # conj, conjugaison, fr-inv
    pass
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['synonymes'], [in_template, ['lien', 'l'], [in_arg, (0, 1) ]]],
        [in_section, ['synonymes'], [in_link]]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )
    

def Antonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['antonymes'], [in_template, ['lien', 'l'], [in_arg, (0, 1) ]]],
        [in_section, ['antonymes'], [in_link]]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['hyperonymes'], [in_template, ['lien', 'l'], [in_arg, (0, 1) ]]],
        [in_section, ['hyperonymes'], [in_link]]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hypernym( lang, term )


def Hyponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['hyponymes'], [in_template, ['lien', 'l'], [in_arg, (0, 1) ]]],
        [in_section, ['hyponymes'], [in_link]]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hyponym( lang, term )


def Meronymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['méronymes'], [in_template, ['lien', 'l'], [in_arg, (0, 1) ]]],
        [in_section, ['méronymes'], [in_link]]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_meronym( lang, term )


def Holonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['holonymes'], [in_template, ['lien', 'l'], [in_arg, (0, 1) ]]],
        [in_section, ['holonymes'], [in_link]]
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
        [in_section, 'related terms', [in_link]],
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
