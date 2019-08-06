# !/usr/bin/python3
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


LANGUAGES = [ "es", "espaniol" ]
LANG_SECTIONS = [ "espaniol", "-es-", "es" ]
TYPE_OF_SPEECH = {
    wt.NOUN          : [ 'forma adjetiva y de sustantivo masculino', 'forma adjetiva y sustantiva', 'forma adjetiva y sustantiva femenina', 'forma adjetiva y sustantiva masculina', 'forma adjetiva y sustantiva masculina y femenina', 'forma adjetiva y sustantivo femenino', 'forma adjetiva, de participio y sustantiva', 'forma adjetiva, sustantiva y de participio', 'forma de sustantivo', 'forma de sustantivo propio femenino', 'forma de sustantivo propio masculino', 'forma sustantiva', 'forma sustantiva ambigua', 'forma sustantiva de género común', 'forma sustantiva femenina', 'forma sustantiva femenina o masculina', 'forma sustantiva femenina y masculina', 'forma sustantiva femenino', 'forma sustantiva maculina', 'forma sustantiva masculina', 'forma sustantiva masculina e interjección', 'forma sustantiva masculina y adjetiva', 'forma sustantiva masculina y femenina', 'forma sustantiva masculíno', 'forma sustantiva neutra', 'forma sustantiva plural', 'forma sustantiva y adjetiva', 'forma sustantiva y adjetiva masculina', 'forma sustantiva y de participio', 'forma sustantiva, adjetiva y de participio', 'forma sustantiva, adjetiva y de pronombre', 'forma sustantivo', 'forma verbal y sustantivo masculino', 'locución sustantiva', 'sustantiva masculino', 'sustantivo', 'sustantivo ', 'sustantivo  femenino', 'sustantivo ambiguo', 'sustantivo animado', 'sustantivo colectivo de genero femenino', 'sustantivo común', 'sustantivo de clase 9', 'sustantivo en [[aposición]]', 'sustantivo femenino', 'sustantivo femenino mutado', 'sustantivo femenino y masculino', 'sustantivo inanimado', 'sustantivo masculino', 'sustantivo masculino mutado', 'sustantivo masculino o femenino', 'sustantivo masculino plural', 'sustantivo masculino y femenino', 'sustantivo masculino\u200e', 'sustantivo neutro', 'sustantivo neutro y masculino', 'sustantivo propio', 'sustantivo verbal masculino', 'sustantivo?', 'sustantivos', 'sustantivos masculinos', 'sustantivo propio masculino' ],
    wt.ADJECTIVE     : [ 'adjectivo', 'adjentivo', 'adjetivio', 'adjetivo', 'adjetivo cardinal', 'adjetivo comparativo', 'adjetivo demostrativo', 'adjetivo indefinido', 'adjetivo indeterminado', 'adjetivo interrogativo', 'adjetivo numeral', 'adjetivo numeral cardinal', 'adjetivo ordinal', 'adjetivo posesivo', 'adjetivo relativo', 'adjetivos', 'forma adjetiva', 'forma adjetiva determinada', 'forma adjetiva femenina', 'forma adjetiva femenina y masculina', 'forma adjetiva masculina', 'forma adjetiva neutra', 'forma adjetiva ordinal', 'forma adjetiva ordinal y partitiva', 'forma adjetiva plural', 'forma adjetiva y de participio', 'forma adjetiva y de pronombre', 'forma adjetiva y de pronombre indeterminado', 'forma adjetiva y de sustantivo masculino', 'forma adjetiva y pronominal', 'forma adjetiva y sustantiva', 'forma adjetiva y sustantiva femenina', 'forma adjetiva y sustantiva masculina', 'forma adjetiva y sustantiva masculina y femenina', 'forma adjetiva y sustantivo femenino', 'forma adjetiva, de participio y sustantiva', 'forma adjetiva, sustantiva y de participio', 'forma adjetival', 'forma adjetivo', 'forma de adjetivo ordinal', 'forma de adjetivo posesivo', 'forma de pronombre y adjetivo demostrativo', 'forma de pronombre y de adjetivo demostrativo', 'forma femenina adjetiva y pronominal', 'forma sustantiva masculina y adjetiva', 'forma sustantiva y adjetiva', 'forma sustantiva y adjetiva masculina', 'forma sustantiva, adjetiva y de participio', 'forma sustantiva, adjetiva y de pronombre', 'forma verbal y adjetiva', 'formas adjetivas', 'locución adjetiva', 'preposición y adjetivo posesivo' ],
    wt.VERB          : [ 'form verbal', 'forma de verbo', 'forma de verbo transitivo', 'forma del verbo', 'forma forma verbal', 'forma verba l', 'forma verbal', 'forma verbal con enclítico', 'forma verbal conjugada', 'forma verbal enclítica', 'forma verbal regularizada', 'forma verbal transitiva', 'forma verbal y adjetiva', 'forma verbal y pronombre enclítico', 'forma verbal y sustantivo masculino', 'formal verbal', 'formas verbales', 'locución verbal', 'proverbios', 'sustantivo verbal masculino', 'verba formal', 'verbo', 'verbo ', 'verbo auxiliar', 'verbo cópula', 'verbo impersonal', 'verbo intransitivo', 'verbo mediopasivo', 'verbo modal', 'verbo pronominal', 'verbo transitivo', 'verbo transitivo o intransitivo', 'verbos', 'werkwoord-verbo' ],
    wt.ADVERB        : [ "''adverbio''", 'adverbio', 'adverbio comparativo', 'adverbio de afirmación', 'adverbio de cantidad', 'adverbio de cantidad ', 'adverbio de duda', 'adverbio de lugar', 'adverbio de modo', 'adverbio de negación', 'adverbio de orden', 'adverbio de tiempo', 'adverbio demostrativo', 'adverbio interrogativo', 'adverbio relativo', 'adverbios', 'forma adverbial', 'locución adverbial' ],
    wt.PREDICATIVE   : [],
    wt.CONJUNCTION   : [ 'conjunción', 'conjunción adversativa', 'conjunción ilativa', 'conjunción interrogativa', 'contracción de conjunción' ],
    wt.PREPOSITION   : [ 'preposición', 'preposición conjugada', 'preposición de ablativo', 'preposición de acusativo', 'preposición de dativo', 'preposición de genitivo', 'preposición y adjetivo posesivo', 'preposición y artículo', 'preposición y pronombre' ],
    wt.PRONOUN       : [ 'forma adjetiva y de pronombre', 'forma adjetiva y de pronombre indeterminado', 'forma adjetiva y pronominal', 'forma de [[pronombre]]', 'forma de pronombre demostrativo', 'forma de pronombre personal', 'forma de pronombre y adjetivo demostrativo', 'forma de pronombre y de adjetivo demostrativo', 'forma femenina adjetiva y pronominal', 'forma pronombre', 'forma pronominal', 'forma pronominal interrogativa', 'forma sustantiva, adjetiva y de pronombre', 'forma verbal y pronombre enclítico', 'formas pronominales', 'preposición y pronombre', 'pronombre', 'pronombre demostrativo', 'pronombre indefinido', 'pronombre indeterminado', 'pronombre interrogativo', 'pronombre personal', 'pronombre personal masculino', 'pronombre posesivo', 'pronombre reflexivo', 'pronombre relativo' ],
    wt.INTERJECTION  : [ 'forma sustantiva masculina e interjección', 'interjección', 'locución interjectiva' ],
    wt.PARTICLE      : [ 'forma adjetiva ordinal y partitiva', 'forma adjetiva y de participio', 'forma adjetiva, de participio y sustantiva', 'forma adjetiva, sustantiva y de participio', 'forma de participio', 'forma participial', 'forma sustantiva y de participio', 'forma sustantiva, adjetiva y de participio', 'participio' ],
    wt.ARTICLE       : [ "article" ],
    wt.NUMERAL       : [ 'adjetivo numeral', 'adjetivo numeral cardinal', 'determinante numeral', 'numeral', 'numeral cardinal' ],
    wt.ABBREV        : ['abbrev'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name if t.arg(0) and t.arg(0).lower().strip() in LANGUAGES else None for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'langue'  : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)),
    'lengua'  : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)),
    'es'      : lambda t: 'es',
})


def is_lang_template(t):
    # {{PT-ES}}
    if t.raw.upper() == t.raw and len(t.name) >= 2 and len(t.name) <= 12 and t.name.endswith("-es"):
        return True

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
    if sec.name in ["bedeutungen"]:
        return True


def Type(search_context, excludes, word):
    sec = search_context
    
    for (tos, section_names) in TYPE_OF_SPEECH.items():
        if sec.name in section_names:
            word.Type = tos
            break


def IsMale(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_name, "masculino"] ,
        [has_flag_in_name, "maschile"] ,
        #[has_template, "g", [has_arg, "m" ]] ,
        #[has_template, "g", [has_arg, "m-p"]] ,
        #[has_template, "m"] ,
        #[has_template, "mf"] ,
        #[has_template, "fm"] ,
        #[has_template, "masculine plural past participle of"] ,
        #[has_template, "masculine plural of"] ,
        #[has_flag_in_text, "''m sing''"] ,
        #[has_flag_in_text, "''m pl''"] ,
        #[has_flag_in_text, "''m inv''"],
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_name, "femenino"] ,
        [has_flag_in_name, "femminile"] ,
        #[has_template, "g", [has_arg, "f" ]] ,
        #[has_template, "g", [has_arg, "f-p"]] ,
        #[has_template, "f"] ,
        #[has_template, "mf"] ,
        #[has_template, "fm"] ,
        #[has_template, "deutsch substantiv übersicht", [has_arg, "Genus", "f"]] ,
        #[has_flag_in_text, "''f sing''"] ,
        #[has_flag_in_text, "''f pl''"] ,
        #[has_flag_in_text, "''f inv''"],
    ):
        word.IsFeminine = True


def IsNeutre(search_context, excludes, word):
    pass


def IsSingle(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "inflect.es.sust.reg"],
        [has_template, "inflect.es.sust.reg-cons"],
        [has_template, "forma verbo", [has_arg, "p", [has_value, [
            "1s", "yo", "2s", "tú", "tu", "2sv", "vos", "2stv", "tú, vos", "2su", "usted", "3s", "primera persona singular", "segunda persona singular", "él", "el", "ella", "tercera persona singular"
        ]]]],
    ):
        word.IsSingle = True
    

def IsPlural(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, "impropia", [has_arg, 0, [has_flag, "forma plural de"]]],
        [has_template, "forma verbo", [has_arg, "p", [has_value, [
            "1p", "nos", "nosotros", "primera persona plural", "2p", "vosotros", "segunda persona plural", "2pu", "ustedes", "3p", "ellos", "ellas", "tercera persona plural"
        ]]]],
    ):
        word.IsPlural = True
    
    
def SingleVariant(search_context, excludes, word):
    for (lang, term) in find_any(search_context, excludes,
        [in_template, "impropia", [in_arg_with_flag_in_value, "forma plural de", [in_link]]]
    ):
        word.SingleVariant = term
        break
        

def PluralVariant(search_context, excludes, word):
    # {{inflect.es.sust.reg-cons}}
    # {{inflect.es.sust.ad-lib}}
    if if_any(search_context, excludes, [has_template, "inflect.es.sust.reg"]):
        if not word.LabelName.endswith('s'):
            word.PluralVariant = word.LabelName + 's'
            
    elif if_any(search_context, excludes, [has_template, "inflect.es.sust.reg-cons"]):
        if not word.LabelName.endswith('es'):
            word.PluralVariant = word.LabelName + 'es'

    elif if_any(search_context, excludes, [has_template, "inflect.es.sust.ad-lib"]):
        for (lang, term) in find_any(search_context, excludes,
            [in_template, "inflect.es.sust.ad-lib", [in_arg, (None, 1)]]
        ):
            word.PluralVariant = term


def MaleVariant(search_context, excludes, word):
    if if_any(search_context, excludes, [has_template, "inflect.es.sust.ad-lib"]):
        for (lang, term) in find_any(search_context, excludes,
            [in_template, "inflect.es.sust.ad-lib", [in_arg, (None, 0)]]
        ):
            word.MaleVariant = term
    

def FemaleVariant(search_context, excludes, word):
    if if_any(search_context, excludes, [has_template, "inflect.es.sust.ad-lib"]):
        for (lang, term) in find_any(search_context, excludes,
            [in_template, "inflect.es.sust.ad-lib", [in_arg, (None, 2)]]
        ):
            word.FemaleVariant = term
    

def IsVerbPast(search_context, excludes, word):
    # {{forma verbo|hacendar|p=1s|t=pretérito|m=indicativo}}.
    if if_any(search_context, excludes, 
        [has_template, "forma verbo", [has_arg, 3,   [has_flag, ["pretérito", "pret", "condicional", "cond"]]]],
        [has_template, "forma verbo", [has_arg, "t", [has_flag, ["pretérito", "pret", "condicional", "cond"]]]],
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    # {{forma verbo|hacendar|p=1s|t=presente|m=indicativo}}.
    if if_any(search_context, excludes, 
        [has_template, "forma verbo", [has_arg, 3,   [has_flag, ["presente", "pres"]]]],
        [has_template, "forma verbo", [has_arg, "t", [has_flag, ["presente", "pres"]]]],
    ):
        word.IsVerbPresent = True
    

def IsVerbFutur(search_context, excludes, word):
    # {{forma verbo|hacendar|p=1s|t=futuro|m=indicativo}}.
    if if_any(search_context, excludes, 
        [has_template, "forma verbo", [has_arg, 3,   [has_flag, ["futuro", "fut", "futuro simple"]]]],
        [has_template, "forma verbo", [has_arg, "t", [has_flag, ["futuro", "fut", "futuro simple"]]]],
    ):
        word.IsVerbFutur = True
    

def Conjugation(search_context, excludes, word):
    def forma_verbo_cb(t, excludes, *args):
        # {{forma verbo|hacendar|p=1s|t=presente|m=indicativo}}.
        lang = t.arg("leng")
        yield (lang, t.arg(0))
        
    def es_v_conj__ie_ue__ar_cb(t, excludes, *args):
        # {{es.v.conj.-ie-ue-.ar|hacend|haciend}}
        lang = t.arg("leng")
        yield (lang, t.arg(0))
        yield (lang, t.arg(1))
        
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "forma verbo", [forma_verbo_cb]],
        [in_template, "f.v", [forma_verbo_cb]],
        [in_template, "es.v.conj.-ie-ue-.ar", [es_v_conj__ie_ue__ar_cb]]
    ):
        if lang is None or lang in LANGUAGES:
            word.add_conjugation(lang, term)
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "sinónimos", [in_arg, (None, [0,1,2,3,4,5,6,7,8,9,10,11,12]) ]],
        [in_template, "sinónimo",  [in_arg, (None, [0,1,2,3,4,5,6,7,8,9,10,11,12]) ]] 
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )


def Antonymy(search_context, excludes, word):
    # === antónimos ===
    # {{l|es|term}}}
    # {{antónimo|claro|term2|term3}}
    for (lang, term) in find_all(search_context, excludes,
        [in_section, "antónimos" , [in_template, "l", [in_arg, (["leng", 0], 1) ]]], 
        [in_template, "antónimo" , [in_arg, (None, [0,1,2,3,4,5,6,7,8,9,10,11,12]) ]], 
        [in_template, "antónimos", [in_arg, (None, [0,1,2,3,4,5,6,7,8,9,10,11,12]) ]] 
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    # {{hipónimo|obrera|reina|zángano}}.
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "hipónimo" , [in_arg, (None, [0,1,2,3,4,5,6,7]) ]], 
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hyponym( lang, term )


def Hyponymy(search_context, excludes, word):
    # {{hiperónimo|himenóptero|insecto}}.
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "hiperónimo" , [in_arg, (None, [0,1,2,3,4,5,6,7]) ]], 
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hypernym( lang, term )


def Meronymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "merónimo" , [in_arg, (None, [0,1,2,3,4,5,6,7]) ]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_meronym( lang, term )


def Holonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "holónimo" , [in_arg, (None, [0,1,2,3,4,5,6,7]) ]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_holonym( lang, term )


def Troponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "tropónimo" , [in_arg, (None, [0,1,2,3,4,5,6,7]) ]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_troponym( lang, term )


def Otherwise(search_context, excludes, word):
    pass


def AlternativeFormsOther(search_context, excludes, word):
    pass


def RelatedTerms(search_context, excludes, word):
    # === Véase también === 
    # * [[...]]
    # {{relacionado|avispa|melipona}}.
    for (lang, term) in find_all(search_context, excludes,
        [in_section, "véase también", [in_link]],
        [in_template, "relacionado", [in_arg, (None, [0,1,2,3,4,5,6,7,8,9,10,11,12])]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)


def Coordinate(search_context, excludes, word):
    pass


def Translation(search_context, excludes, word):
    # === Traducciones === 
    # {{trad|en|cat}}
    # {{t+|fr|ongle|m}}
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "trad", [in_arg, (["lang", "leng", 0], 1)]],
        [in_template, "t"   , [in_arg, (["lang", "leng", 0], 1)]],
        [in_template, "t-simple", [in_arg, (["lang", "leng", 0], 1)]],
        [in_template, "t+"  , [in_t_plus]],
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
