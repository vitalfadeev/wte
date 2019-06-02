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


LANGUAGES = [ "pt", "português" ]
LANG_SECTIONS = [ "pt", "-pt-", "português", "-mwl-" ] # "translingual"
TYPE_OF_SPEECH = {
    wt.NOUN          : ['#substantivo provençal', 'adjetivo e substantivo', 'adjetivo/substantivo', 'balear#substantivo balear  e  valenciano', 'categoria:substantivo (português)  substantivo', 'como substantivo', 'ficheiro:open_book_01.svg 22px  substantivo categoria:substantivo (espanhol)', 'fora de substantivo', 'forma de substantivo', 'forma de substantivo 1', 'forma de substantivo 2', 'forma de substantivo 3', 'forma de substantivo1', 'forma de substantivo2', 'froma de substantivo', 'imagem:open book 01.svg 22px  substantivo', 'pronome substantivo', 'substantivo', "substantivo  ''feminino''", "substantivo  ''masculino''", 'substantivo  (1)', 'substantivo  (2)', 'substantivo  (3)', 'substantivo  1', 'substantivo  2', 'substantivo  3', 'substantivo  4', 'substantivo  próprio', "substantivo (''particípio passivo'')", 'substantivo (2)', 'substantivo 1', 'substantivo 2', 'substantivo 3', 'substantivo 4', 'substantivo 5', 'substantivo adjetivo', 'substantivo categoria:substantivo (português)', 'substantivo de dois gêneros', 'substantivo e advérbio', 'substantivo feminino plural', 'substantivo masculino', 'substantivo próprio', "substantivo,  ''feminino''", "substantivo,  ''masculino'' categoria:substantivo (português)", "substantivo,  ''próprio''", "substantivo,  ''próprio'' categoria:substantivo (português)", 'substantivo,  categoria:substantivo (português)', "substantivo, ''feminino''", 'substantivo1', 'substantivo2', 'substantivo3', 'substantivo>', 'substantivoe', 'substantivoo 1', 'substantivos', 'substantivotivo', 'substantivo²', 'substantivo³', 'substantivo¹'],
    wt.ADJECTIVE     : ['adjectivo', 'adjektivo', 'adjentivo', 'adjetiivo', 'adjetivo', 'adjetivo 1', 'adjetivo 2', 'adjetivo 3', 'adjetivo e substantivo', 'adjetivo substantivado', 'adjetivo/pronome/advérbio', 'adjetivo/substantivo', 'adjetivo1', 'adjetivo2', 'adjetivo3', 'adjetivos', 'adjetivotivo', 'adjetvo', 'como adjetivo', 'forma de adjectivo', 'forma de adjetivo', 'forma de adjetivo 1', 'forma de adjetivo 2', 'forms de adjetivo', 'locução adjetiva', 'pronome adjetivo', 'substantivo adjetivo', 'verbo adjetivo'],
    wt.VERB          : ['verbo', "verbo '''1'''", 'verbo 1', 'verbo 2', 'verbo 3', 'verbo 4', 'verbo adjetivo', 'verbo auxiliar', 'verbos', 'verbo²', 'verbo¹', 'forma verbal'],
    wt.ADVERB        : ['adverbio', 'locução adverbial'],
    wt.PREDICATIVE   : [],
    wt.CONJUNCTION   : ['conjunção', 'conjunção 1', 'conjunção 2'],
    wt.PREPOSITION   : ['outras preposições', 'preposição'],
    wt.PRONOUN       : ['adjetivo/pronome/advérbio', 'forma de pronome', 'forma pronominal', 'pronome', 'pronome 1', 'pronome 2', 'pronome 3', 'pronome adjetivo', 'pronome demostrativo', 'pronome indefinido plural', 'pronome pessoais', 'pronome pessoal', 'pronome substantivo', 'pronomes', 'pronomes de género neutro sugeridos', 'pronomes demonstrativos', 'pronomes oblíquos', 'pronomes pessoais'],
    wt.INTERJECTION  : ['interjeiçao', 'interjeição', 'interjeção'],
    wt.PARTICLE      : [],
    wt.ARTICLE       : ['artigo'],
    wt.NUMERAL       : ['forma de numeral', 'numeral', 'numeral cardinal', 'numeral fracionário', 'numeral multiplicativo', 'numeral ordinal', 'outros numerais'],
    wt.ABBREV        : ['abbrev'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name if t.arg(0) and t.arg(0).lower().strip() in LANGUAGES else None for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'língua'  : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)),
    '-pt-'    : lambda t: "-pt-",
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
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['m', 'mp']]],
            [has_arg, 0, [has_value, ['m', 'mp']]]
        ],
        [has_template, 'm'], 
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['f', 'fp']]],
            [has_arg, 1, [has_value, ['f', 'fp']]]
        ],
        [has_template, 'f'], 
    ):
        word.IsMale = True


def IsNeutre(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['n', 'np', 'ns', 'n2n']]]
        ],
        [has_template, 'n'], 
    ):
        word.IsNeutre = True


def IsSingle(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['s', 'fs', 'ms', 'ns', 'cs', '2gs', 'c2gs', '1ps', '2ps', '3ps']]],
            [has_arg, 1, [has_value, ['s', 'fs', 'ms', 'ns', 'cs', '2gs', 'c2gs', '1ps', '2ps', '3ps']]],
            [has_arg, 2, [has_value, ['s', 'fs', 'ms', 'ns', 'cs', '2gs', 'c2gs', '1ps', '2ps', '3ps']]],
        ],
        [has_flag_in_explaination, 'singular']
    ):
        word.IsSingle = True


def IsPlural(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['p', 'fp', 'mp', 'np', 'cp', '2gp', 'c2gp', '1pp', '2pp', '3pp']]],
            [has_arg, 1, [has_value, ['p', 'fp', 'mp', 'np', 'cp', '2gp', 'c2gp', '1pp', '2pp', '3pp']]],
            [has_arg, 2, [has_value, ['p', 'fp', 'mp', 'np', 'cp', '2gp', 'c2gp', '1pp', '2pp', '3pp']]],
        ],
        [has_flag_in_explaination, 'plural']
    ):
        word.IsPlural = True
    
    
def SingleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['ms', 'fs', 'msa', 'fsa', 'msd', 'fsd']) ],
        ]
    ):
        if lang is None or lang in LANGUAGES:
            word.SingleVariant = term
            break
        

def PluralVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['mp', 'fp', 'mpa', 'fpa', 'mpd', 'fpd']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.PluralVariant = term
            break


def MaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['avi-for-fle'],
            [in_arg, (None, 0) ],
        ],
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['ms', 'msa', 'msd']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.MaleVariant = term
            break


def FemaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['fs', 'fsa', 'fsd']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.FemaleVariant = term
            break
    

def IsVerbPast(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_explaination, ["passato"]] ,
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_explaination, "presente", 'pretérito imperfeito'] ,
    ):
        word.IsVerbPresent = True
    

def IsVerbFutur(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_flag_in_text, "futuro"] ,
    ):
        word.IsVerbFutur = True    
    

def Conjugation(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['conj.gl', 'conj.gl.ar', 'conj.gl.er'],
            [in_arg, (None, [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_conjugation( lang, term )
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-sino-', 'sinóinimos', 'sinónimo', 'sinónimos', 'sinónimos 2', 'sinónimos 3', 'sinónimoss', 'sinônimo/sinónimo', 'sinônimos/sinónimos', 'sinônimos', 'sinô(ó)nimo', 'sinônimo', 'sinônimo imperfeito', 'sinônimo perfeito', 'sinônimo/sinónimo', 'sinônimos', 'sinônimos (1)', 'sinônimos (2)', 'sinônimos / variações', 'sinônimos de 1, (chama)', 'sinôninimos', 'sinôninos', 'sinônímos'],
            [in_template, ['link', 'l', 'lb'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )
    

def Antonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['antônimo', 'antônimos', 'antônimos (1)', 'antônimos (2)'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['hipernímias'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hypernym( lang, term )


def Hyponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['hiponímias'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hyponym( lang, term )


def Meronymy(search_context, excludes, word):
    pass


def Holonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['holonímias'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_holonym( lang, term )

    
def Troponymy(search_context, excludes, word):
    pass


def Otherwise(search_context, excludes, word):
    pass


def AlternativeFormsOther(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['ms', 'mp', 'fs', 'fp', 'msa', 'mpa', 'fsa', 'fpa', 'msd', 'mpd', 'fsd', 'fpd', 'col']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_alternative_form( lang, term )    


def RelatedTerms(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['-rel-', 'termos correlatos', 'termos relacionados', 'verbetes relacionados', 'verbetes relacionados ao natal', 'verbetes relativos'], 
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)
    

def Coordinate(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, 'termos coordenados (koipônimos)', 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_coordinate( lang, term )


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
