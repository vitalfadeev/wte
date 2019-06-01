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
    has_template, has_template_with_flag, \
    has_arg, has_flag, has_value, has_arg_and_value_contain, has_arg_with_flag_in_name, \
    find_terms, \
    get_label_type, find_explainations, \
    term0_cb, term1_cb, lang0_term1_cb, lang0_term2_cb, t_plus_cb, w_cb, alter_cb, en_conj_cb, \
    find_all, find_any, \
    in_section, in_template, in_arg, in_arg_with_flag_in_value, in_link, in_t_plus, in_callback


LANGUAGES = [ "en", "english" ]
LANG_SECTIONS = [ "english", "-en-", "en", "translingual" ]
TYPE_OF_SPEECH = {
    wt.NOUN          : ['noun', 'noun 1', 'noun 2', 'noun 3', 'proper noun', 'proper noun 1', 'proper noun 2'],
    wt.ADJECTIVE     : ['adjective'],
    wt.VERB          : ['derived compound verbs', 'preverb', 'proverbs', 'verb', 'verb 1', 'verb 2', 'verb 3', 'verb root'],
    wt.ADVERB        : ['adverb'],
    wt.PREDICATIVE   : ['predicative'],
    wt.CONJUNCTION   : ['conjugation', 'conjugation 1', 'conjugation 2'],
    wt.PREPOSITION   : ['preposition', 'prepositional phrase', 'prepositional pronoun'],
    wt.PRONOUN       : ['prepositional pronoun', 'pronoun'],
    wt.INTERJECTION  : ['interjection', 'interjection 1', 'interjection 2'],
    wt.PARTICLE      : ['participle', 'participles', 'particle', 'particle 1', 'particle 2'],
    wt.ARTICLE       : ['article'],
    wt.NUMERAL       : ['numeral'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name if t.arg(0) and t.arg(0).lower().strip() in LANGUAGES else None for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: t.arg(0).lower() if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'language': lambda t: t.arg(0).lower(),
    'en'      : lambda t: 'en',
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


def en_noun(t, excludes, label, miners=None):
    """
    {{en-noun}}
    {{en-noun|es}}
    {{en-noun|...}}
    {{en-noun|...|...}}

    out: (single, [plural], is_uncountable)
    """
    s = label
    p = []
    is_uncountable = False

    # http://en.wiktionary.org/wiki/Template:en-noun
    head = t.arg("head")
    head = head if head else label
    p1 = t.arg(0)
    p2 = t.arg(1)

    if p1 == "-":
        # uncountable
        is_uncountable = True

        if p2 == "s":
            # ends by s
            yield (None, head + "s")

        elif p2 is not None:
            # word
            yield (None, p2)

    elif p1 == "s":
        yield (None, head + "s")

    elif p1 == "es":
        # add es
        yield (None, head + "es")

    elif p1 is not None:
        # use term
        yield (None, p1)

    elif p1 is None and p2 is None:
        yield (None, head + "s")


def en_verb(t, excludes, label, miners=None):
    v1 = t.arg(0)
    v2 = t.arg(1)
    v3 = t.arg(1)
    head = t.arg("head")
    head = head if head is not None else label
    acount = len(list(t.positional_args()))
    
    if acount == 0:
        yield (None, head+'s')
        yield (None, head+'ed')
        yield (None, head+'ing')

    elif acount == 1:
        head = v1
        yield (None, head+'s')
        yield (None, head+'ed')
        yield (None, head+'ing')
    
    elif acount == 2:
        if v2 == 'es':
            yield (None, v1+'es')
            
        elif v2 == 'd':
            yield (None, v1+'d')

        elif v2 == 'ing':
            yield (None, v1+'ing')

    elif acount == 3:
        if v2 == 's':
            yield (None, v1+'s'+v3)

        elif v2 == 'i':
            yield (None, v1+'i'+v3)

        elif v2 == 'y':
            yield (None, v1+'y'+v3)

        elif v2 == 'k':
            yield (None, v1+'k'+v3)
            
        else:
            if v1 != '-':
                yield (None, v1)
            if v2 != '-':
                yield (None, v2)
            if v3 != '-':
                yield (None, v3)


def en_adj(t, excludes, label, miners=None):
    v1 = t.arg(0)
    v2 = t.arg(1)
    v3 = t.arg(1)
    head = t.arg("head")
    head = head if head is not None else label
    acount = len(list(t.positional_args()))
    
    if acount == 0:
        yield (None, 'more '+head)
        yield (None, 'most '+head)

    elif acount == 1:
        if v1 == 'er':
            yield (None, 'more '+head+'er')
            yield (None, 'most '+head+'er')
        elif v1 == '-':
            pass
        elif v1 == '?':
            pass
        elif v1 == '+':
            pass
        else:
            yield (None, v1)


def Type(search_context, excludes, word):
    sec = search_context
    
    for (tos, section_names) in TYPE_OF_SPEECH.items():
        if sec.name in section_names:
            word.Type = tos
            break


def IsMale(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "g", [has_value, "m" ]] ,
        [has_template, "g", [has_value, "m-p"]] ,
        [has_template, "masculine plural past participle of"] ,
        [has_template, "masculine plural of"] ,
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "g", [has_value, "f" ]] ,
        [has_template, "g", [has_value, "f-p"]] ,
        [has_template, ['feminine noun of', 'feminine of', 'feminine plural of', 'feminine singular of']] ,
    ):
        word.IsFeminine = True


def IsNeutre(search_context, excludes, word):
    pass


def IsSingle(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['accusative singular of', 'dative singular of', 'en-archaic second-person singular of', 'en-archaic second-person singular past of', 'en-archaic third-person singular of', 'en-third person singular of', 'en-third-person singular of', 'enm-first-person singular of', 'enm-first/third-person singular past of', 'enm-second-person singular of', 'enm-second-person singular past of', 'enm-singular subjunctive of', 'enm-singular subjunctive past of', 'enm-third-person singular of', 'feminine singular of', 'feminine singular past participle of', 'genitive singular definite of', 'genitive singular indefinite of', 'genitive singular of', 'neuter singular of', 'neuter singular past participle of', 'sco-third-person singular of', 'singular definite of', 'singular indefinite of', 'singular of', 'vocative singular of']],        
        [has_template, "fi-form of", [has_arg, "pl", [has_value, "singular"]]],
        [has_template, 'en-noun'],        
    ):
        word.IsSingle = True


def IsPlural(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['accusative singular of', 'dative singular of', 'en-archaic second-person singular of', 'en-archaic second-person singular past of', 'en-archaic third-person singular of', 'en-third person singular of', 'en-third-person singular of', 'enm-first-person singular of', 'enm-first/third-person singular past of', 'enm-second-person singular of', 'enm-second-person singular past of', 'enm-singular subjunctive of', 'enm-singular subjunctive past of', 'enm-third-person singular of', 'feminine singular of', 'feminine singular past participle of', 'genitive singular definite of', 'genitive singular indefinite of', 'genitive singular of', 'neuter singular of', 'neuter singular past participle of', 'sco-third-person singular of', 'singular definite of', 'singular indefinite of', 'singular of', 'vocative singular of']],        
        [has_template, "fi-form of", [has_arg, "pl", [has_value, "plural"]]],
        [has_template, 'en-plural noun'],        
    ):
        word.IsPlural = True
    
    
def SingleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'en-plural noun', [in_arg, (None, 'sg')]],
    ):
        word.SingleVariant = term
        break
        

def PluralVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'en-noun', [en_noun, word.LabelName]],
    ):
        word.PluralVariant = term
        break


def MaleVariant(search_context, excludes, word):
    pass
    

def FemaleVariant(search_context, excludes, word):
    pass
    

def IsVerbPast(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "fi-form of", [has_arg, "tense", [has_value, "past"]]],
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "fi-form of", [has_arg, "tense", [has_value, ["present", "present connegative"]]]],
    ):
        word.IsVerbPresent = True
    

def IsVerbFutur(search_context, excludes, word):
    pass
    

def Conjugation(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'en-verb', [en_verb, word.LabelName]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_conjugation( lang, term )
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ["syn", 'synonym of'], [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, ['synonym', 'synonyms'], [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, ['synonym', 'synonyms'], [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
        [in_template, 'sense', [in_link]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )
    

def Antonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "antonyms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, ['antonym', 'antonyms'], [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, ['antonym', 'antonyms'], [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "hypernyms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, 'hypernyms', [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, 'hypernyms', [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hypernym( lang, term )


def Hyponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "hyponyms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, 'hyponyms', [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, 'hyponyms', [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hyponym( lang, term )


def Meronymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "meronyms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, 'meronyms', [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, 'meronyms', [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_meronym( lang, term )


def Holonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "holonyms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, 'holonyms', [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, 'holonyms', [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_holonym( lang, term )
    

def Troponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "troponyms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, 'troponyms', [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
        [in_section, 'troponyms', [in_template, 'wikipedia', [in_arg, (None, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_troponym( lang, term )


def Otherwise(search_context, excludes, word):
    pass


def AlternativeFormsOther(search_context, excludes, word):
    # {{en-adv}}
    # {{en-adj}}
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['en-adv','en-adj'], [en_adj, word.LabelName]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_alternative_form( lang, term )


def RelatedTerms(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, 'related terms', [in_link]],
        [in_template, ['see', 'also'], [in_arg, ([0,1,2,3,4,5,6,7]) ]],
        [in_template, 'cog', [in_arg, (0, 1) ]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)
    

def Coordinate(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "coordinate terms", [in_arg, (0, [1,2,3,4,5,6,7]) ]],
        [in_section, 'coordinate terms', [in_template, ['l', 'lb', 'label', 'm', 'link'], [in_arg, (0, 1) ]]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_coordinate( lang, term )


def Translation(search_context, excludes, word):
    # {{trad|en|cat}}
    # {{t+|fr|ongle|m}}
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "trad", [in_arg, (["lang", 0], 1)]],
        [in_template, "t"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "t-simple", [in_arg, (["lang", 0], 1)]],
        [in_template, "t+"  , [in_t_plus]],
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
