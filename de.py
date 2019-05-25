#!/usr/bin/python3
# -*- coding: utf-8 -*-

from wte import Word, KEYS, WORD_TYPES, get_label_type
from wikoo import Li, Template, Section, Link
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found
from helpers import merge_two_dicts, check_flag


# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
languages = ["de", "deutsch"]
lang_sections = ["deutsch", "{{-de-}}", "{{sprache|deutsch}}", "sprache"]
section_templates = [
    "worttrennung",
    "aussprache",
    "bedeutungen", 
    "herkunft",
    "synonyme",
    "gegenwörter",
    "beispiele",
    "redewendungen",
    "charakteristische wortkombinationen",
    "wortbildungen",
    "referenzen",
    "quellen",
    "männliche wortformen",
    "weibliche wortformen",
    "verkleinerungsformen",
    "oberbegriffe",
    "unterbegriffe",
    "beispiele",
    "redewendungen",
    "sprichwörter",
    "charakteristische wortkombinationen",
    "wortbildungen",
    "referenzen",
    "quellen",
    "übersetzungen",
]


# Type of speech sections
# Wortart - tos
# == butter ({{Sprache|Deutsch}}) ==
# === {{Wortart|Konjugierte Form|Deutsch}} ===
tos_sections = {
    WORD_TYPES.NOUN: [
        "substantiv",
        
        "noun",
        "noun 1",
        "noun 2",
        "pronoun",
        "proper noun",
        "substantif"                    ,
        "nombre"                        ,
        "nom"                           ,
        "nom commun"                    ,
        "nom de famille"                ,
        "nom propre"                    ,
        "{{s|nom|fr}}"                  ,
        "{{s|nom commun|fr}}"           ,
        "{{s|nom de famille|fr|num=1}}" ,
        "{{s|nom de famille|fr|num=2}}" ,
        "{{s|nom de famille|fr}}"       ,
        "{{s|nom propre|fr|num=1}}"     ,
        "{{s|nom propre|fr|num=2}}"     ,
        "{{s|nom propre|fr|num=3}}"     ,
        "{{s|nom propre|fr|num=4}}"     ,
        "{{s|nom propre|fr}}"           ,
        "{{s|nom|fr|flexion|num=1}}"    ,
        "{{s|nom|fr|flexion|num=2}}"    ,
        "{{s|nom|fr|flexion|num=3}}"    ,
        "{{s|nom|fr|flexion|num=4}}"    ,
        "{{s|nom|fr|flexion|}}"         ,
        "{{s|nom|fr|flexion}}"          ,
        "{{s|nom|fr|nom=1}}"            ,
        "{{s|nom|fr|nom=2}}"            ,
        "{{s|nom|fr|num = 1}}"          ,
        "{{s|nom|fr|num =2}}"           ,
        "{{s|nom|fr|num=1|flexion}}"    ,
        "{{s|nom|fr|num=1}}"            ,
        "{{s|nom|fr|num=2|flexion}}"    ,
        "{{s|nom|fr|num=2}}"            ,
        "{{s|nom|fr|num=3|flexion}}"    ,
        "{{s|nom|fr|num=3}}"            ,
        "{{s|nom|fr|num=4}}"            ,
        "{{s|nom|fr|num=5}}"            ,
        "{{s|nom|fr|num=6}}"            ,
        "{{s|nom|fr|num=7}}"            ,
        "{{s|nom|fr|num=8}}"            ,
        "{{s|nom|fr}}"                  ,
    ],
    WORD_TYPES.ADJECTIVE: [
        "adjektiv",
        
        "abbreviation",
        "adjective",
        "adjetivo"                              ,
        "adjectif"                              ,
        "adjectif démonstratif",
        "adjectif indéfini",
        "adjectif numéral",
        "adjectif possessif",
        "adjectif relatif",
        "adj",
        "{{s|adjectif démonstratif|fr}}"        ,
        "{{s|adjectif indéfini|fr}}"            ,
        "{{s|adjectif indéfini|fr|flexion}}"    ,
        "{{s|adjectif numéral|fr|flexion}}"     ,
        "{{s|adjectif numéral|fr}}"             ,
        "{{s|adjectif possessif|fr|flexion}}"   ,
        "{{s|adjectif possessif|fr}}"           ,
        "{{s|adjectif relatif|fr}}"             ,
        "{{s|adjectif|fr|flexion|num=1}}"       ,
        "{{s|adjectif|fr|flexion|num=2}}"       ,
        "{{s|adjectif|fr|flexion}}"             ,
        "{{s|adjectif|fr|num=1}}"               ,
        "{{s|adjectif|fr|num=2}}"               ,
        "{{s|adjectif|fr|num=3}}"               ,
        "{{s|adjectif|fr}}"                     ,
        "{{s|adj|fr|flexion}}"                  ,
        "{{s|adj|fr}}"                          ,
    ],
    WORD_TYPES.VERB: [
        "verb",
        
        "verbo"                         ,
        "verbe"                         ,
        "{{s|verbe|fr|flexion|num=1}}"  ,
        "{{s|verbe|fr|flexion|num=2}}"  ,
        "{{s|verbe|fr|flexion|num=3}}"  ,
        "{{s|verbe|fr|flexion}}"        ,
        "{{s|verbe|fr|num=1}}"          ,
        "{{s|verbe|fr|num=2}}"          ,
        "{{s|verbe|fr|num=3}}"          ,
        "{{s|verbe|fr|num=4}}"          ,
        "{{s|verbe|fr}}"                ,
    ],
    WORD_TYPES.ADVERB: [
        "adverb",
        
        "adverb",
        "adverbe",
        "adverbe interrogatif",
        "adverbe interrogatif",
        "adv",
        "{{s|adverbe interrogatif|fr}}"         ,
        "{{s|adverbe relatif|fr}}"              ,
        "{{s|adverbe|fr|flexion}}"              ,
        "{{s|adverbe|fr|num=1}}"                ,
        "{{s|adverbe|fr|num=2}}"                ,
        "{{s|adverbe|fr}}"                      ,
        "{{s|adv|fr}}"                          ,
        "adverbio"          ,
        "{{s|adverbe|fr}}"  ,
        "proverbe"          ,
    ],
    WORD_TYPES.PREDICATIVE: [
        "prädikativ",
        
        "predicative"
    ],
    WORD_TYPES.CONJUNCTION: [
        "konjunktion",
        "konjugierte Form",
        
        "conjugation",
        "conjunción"                            ,
        "conjonction"                           ,
        "conjonction de coordination"           ,
        "{{s|conjonction de coordination|fr}}"  ,
        "{{s|conjonction|fr|num=1}}"            ,
        "{{s|conjonction|fr|num=2}}"            ,
        "{{s|conjonction|fr}}"                  ,
    ],
    WORD_TYPES.PREPOSITION: [
        "präposition",
        
        "preposition",
        "preposición"                   ,
        "préposition"                   ,
        "{{s|préposition|fr|flexion}}"  ,
        "{{s|préposition|fr|num=1}}"    ,
        "{{s|préposition|fr|num=2}}"    ,
        "{{s|préposition|fr}}"          ,
    ],
    WORD_TYPES.PRONOUN: [
        "pronomen",
        
        "pronoun",
        "pronombre"                     ,
        "pronom"                        ,
        "pronom démonstratif"           ,
        "pronom indéfini"               ,
        "pronom interrogatif"           ,
        "pronom personnel"              ,
        "pronom relatif"                ,
        "prénom"                        ,
        "{{s|pronom démonstratif|fr|flexion}}" ,
        "{{s|pronom démonstratif|fr}}"  ,
        "{{s|pronom indéfini|fr|flexion}}" ,
        "{{s|pronom indéfini|fr}}"      ,
        "{{s|pronom interrogatif|fr|flexion}}" ,
        "{{s|pronom interrogatif|fr}}"  ,
        "{{s|pronom personnel|fr|num=1}}" ,
        "{{s|pronom personnel|fr|num=2}}" ,
        "{{s|pronom personnel|fr}}"     ,
        "{{s|pronom relatif|fr|flexion}}" ,
        "{{s|pronom relatif|fr}}"       ,
        "{{s|pronom|fr}}"               ,
        "{{s|prénom|fr|genre=f|num=1}}" ,
        "{{s|prénom|fr|genre=f|num=2}}" ,
        "{{s|prénom|fr|genre=f}}"       ,
        "{{s|prénom|fr|genre=mf}}"      ,
        "{{s|prénom|fr|genre=m|num=1}}" ,
        "{{s|prénom|fr|genre=m|num=2}}" ,
        "{{s|prénom|fr|genre=m}}"       ,
        "{{s|prénom|fr}}"               ,
    ],
    WORD_TYPES.INTERJECTION: [
        "interjektion",
        
        "interjection",
        "interjection 1",
        "interjection 2",
        "interjección"              ,
        "{{s|interjection|fr}}"     ,
    ],
    WORD_TYPES.PARTICLE: [
        "partikel",
        
        "particle",
        "partícula"             ,
        "particule"             ,
        "{{s|particule|fr}}"    ,
    ],
    WORD_TYPES.ARTICLE: [
        "artikel",
        
        "article",
        "artículo"                          ,
        "article"                           ,
        "article défini"                    ,
        "article défini"                    ,
        "article indéfini"                  ,
        "article indéfini"                  ,
        "{{s|article défini|fr|flexion}}"   ,
        "{{s|article défini|fr}}"           ,
        "{{s|article indéfini|fr|flexion}}" ,
        "{{s|article indéfini|fr}}"         ,
        "{{s|article|fr}}"                  ,
    ],
    WORD_TYPES.NUMERAL: [
        "number",
        "numeral",
        "numéral"               ,
        "onomatopée"            ,
        "{{s|onomatopée|fr}}"   ,
    ]
}


# translation sections
translation_sections = [
    "übersetzungen", 
    
    "translations", 
    "translation",
    "traductions",
    "{{s|traductions}}",
    "{{s|traductions à trier}}",
    "{{s|transcriptions}}"
]

# synonym sections
synonym_sections = [
    "synonyme",
    "{{synonyme}}",
    
    "synonyms",
    "synonym",
    "synonyme",
    "synonymes",
    "{{s|synonymes}}"
]

# conjugation sections
conjugation_sections = [
    "conjugation",
    "{{s|conjonction|fr|num=1}}",
    "{{s|conjonction|fr|num=2}}",
    "{{s|conjonction|fr}}",
]

# antonymy_sections
antonymy_sections = [
    "gegenwörter",
    "{{Gegenwörter}}",
    
    "antonyms",
    "{{s|antonymes}}"
]

# hypernymy_sections
hypernymy_sections = [
    "hypernyms",
    "{{s|hyperonymes}}"
]

# hyponymy_sections
hyponymy_sections = [
    "hyponyms",
    "{{s|hyponymes}}",
]

# meronymy_sections
meronymy_sections = [
    "meronyms"
]

# holonymy_sections
holonymy_sections = [
    "holonyms",
    "{{s|holonymes}}",
]

# troponymy_sections
troponymy_sections = [
    "troponyms",
    "{{s|troponymes}}"
]

# alternative_forms_sections
alternative_forms_sections = [
    "alternative forms"
]

# related_sections
related_sections = [
    "related terms"
]

# coordinate_sections
coordinate_sections = [
    "coordinate terms",
    "{{s|conjonction de coordination|fr}}",
]

def Deutsch_Substantiv(t):
    g = t.arg("Genus")
    if g == "f": # female
        pass
    
    si = t.arg("Nominativ Singular")
    pi = t.arg("Nominativ Plural")
    sr = t.arg("Genitiv Singular")
    pr = t.arg("Genitiv Plural")
    sd = t.arg("Dativ Singular")
    pd = t.arg("Dativ Plural")
    sa = t.arg("Akkusativ Singular")
    pa = t.arg("Akkusativ Plural")
    
    result = [si, pi, sr, pr, sd, pd, sa, pa]
    result = [ s.strip() for s in result if s ]
    
    return result


def Deutsch_Verb(t):
    # {{Deutsch Verb Übersicht
    # |Präsens_ich=mache
    # |Präsens_du=machst
    # |Präsens_er, sie, es=macht
    # |Präteritum_ich=machte
    # |Partizip II=gemacht
    # |Konjunktiv II_ich=machte
    # |Imperativ Singular=mache
    # |Imperativ Singular*=mach
    # |Imperativ Plural=macht
    # |Hilfsverb=haben
    # }}
    
    present1 = t.arg("Präsens_ich")
    present2 = t.arg("Präsen_du")
    present3 = t.arg("Präsens_er")
    present4 = t.arg("Präteritum_ich")
    past = t.arg("Partizip II")
    cont = t.arg("Konjunktiv II_ich")
    si = t.arg("Imperativ Singular")
    si2 = t.arg("Imperativ Singular*")
    pi = t.arg("Imperativ Plural")
    helper = t.arg("Hilfsverb")
    
    result = [present1, present2, present3, present4, past, cont, si, si2, pi, helper]
    result = [ s.strip() for s in result if s ]
    
    return result
    

def t_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def en_conj_cb(t):
    basic_form = t.arg(0)
    simple_past_form = t.arg(1)
    past_participle = t.arg(2)
    present_participle = t.arg(3)
    simple_present_third_person_form = t.arg(4)
    yield (None, basic_form)
    yield (None, simple_past_form)
    yield (None, past_participle)
    yield (None, present_participle)
    yield (None, simple_present_third_person_form)


def en_conj_simple_cb(t):
    None


conjugation_templates = {
    "en-conj": en_conj_cb,
    # "en-conj-simple"    : en_conj_simple_cb,
}


def L_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def jump_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def l_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def lb_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def m_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def soplink_cb(t):
    lang = None
    term = t.arg(0)
    yield (lang, term)


def w_cb(t):
    lang = None
    term = t.arg(0)
    if term == t.arg("lang"):
        term = t.arg(1)
    yield (lang, term)


def pedia_cb(t):
    lang = None
    term = t.arg(0)
    yield (lang, term)


def wikipedia_cb(t):
    lang = None
    term = t.arg(0)
    yield (lang, term)


def wikispecies_cb(t):
    lang = None
    term = t.arg(0)
    yield (lang, term)


def synonym_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def word_Hypernyms_cb(t):
    term = t.name.split(" ")[0]
    yield (None, term)


def alter_cb(t):
    lang = t.arg(0)
    args = list(t.args())
    if len(args) > 1:
        for a in args[1:]:
            term = a.get_value()
            if len(term.strip()) == 0:
                break
            yield (lang, term)


def alternative_form_of_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def cog_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def en_adj_cb(t):
    None


def form_of_cb(t):
    lang = None
    term = t.arg(2)
    yield (lang, term)


def given_name_cb(t):
    lang = None
    term = t.arg(1)
    yield (lang, term)


def head_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def pedlink_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def rhymes_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def rootsee_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


def en_noun(t, label):
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
            p.append(head + "s")

        elif p2 is not None:
            # word
            p.append(p2)

    elif p1 == "s":
        p.append(head + "s")

    elif p1 == "es":
        # add es
        p.append(head + "es")

    elif p1 is not None:
        # use term
        p.append(p1)

    elif p1 is None and p2 is None:
        p.append(head + "s")

    for i, a in enumerate(t.args()):
        key = a.get_name()
        if not key:
            if i == 0:
                continue

            p.append(a.get_value())

    return (s, p, is_uncountable)


common_templates = {
    "cog": cog_cb,
    "l": l_cb,  # {{l|cs|háček}} | {{l|en|go|went}} - word go section #went
    "lb": lb_cb,  # {{label|en|foobarbazbip}}
    "lbl": lb_cb,
    "l-self": l_cb,
    "m-self": l_cb,
    "label": l_cb,
    "m": m_cb,  # {{m|en|word}}
    "rootsee": rootsee_cb,
    "jump": jump_cb,  # {{jump|fr|combover|s|a}}
    "link": l_cb,
    "soplink": soplink_cb,  # {{soplink|foo|/|bar|baz|-} → foo/bar baz-
    "pedlink": pedlink_cb,
    "pedia": pedia_cb,
    "w": w_cb, # *{{w|William Shakespeare|Shakespeare}} | *{{w|William Shakespeare|Shakespeare|lang=fr}} | *{{w|lang=fr|William Shakespeare|Shakespeare}}
    "wikipedia": wikipedia_cb,  # {{wikipedia|article|link title}}
    "wikispecies": wikispecies_cb,
 }

translations_templates = {
    "ü"           : t_cb,
    "üt"          : t_cb,
    
    "t"           : t_cb,
    "t*"          : t_cb,
    "t+"          : t_cb,
    "t+check"     : t_cb,
    "t+tt"        : t_cb,
    "t-check"     : t_cb,
    "t-check-egy" : t_cb,
    "t-egy"       : t_cb,
    "t-f"         : t_cb,
    "t-image"     : t_cb,
    "t-needed"    : t_cb,
    "t-sile"      : t_cb,
    "t-simple"    : t_cb,
    "t-tpi"       : t_cb,
    "trad+"       : t_cb,
    "trad-"       : t_cb,
    "trad--"      : t_cb,
    "trad"        : t_cb,
}

synonyms_templates = merge_two_dicts( common_templates, {
    "s": synonym_cb,
    "syn": synonym_cb,
    "synonym of": synonym_cb,
})

antonymy_templates = merge_two_dicts( common_templates, {
})

hypernymy_templates = merge_two_dicts( common_templates, {
})

hyponym_templates = merge_two_dicts( common_templates, {
})

meronymy_templates = merge_two_dicts( common_templates, {
})

holonymy_templates = merge_two_dicts( common_templates, {
})

troponymy_templates = merge_two_dicts( common_templates, {
})


alternative_forms_templates = merge_two_dicts( common_templates, {
    "alter": alter_cb,
    "alternative form of": alternative_form_of_cb,
    # "en-adj"    : en_adj_cb,
    "en-conj": en_conj_cb,
    # "fi-alt-personal",
    "form of": form_of_cb,  # {{form of|en|alternative form|word}}
    "given name": given_name_cb,  # {{given name|en|male}}.
    "head": head_cb,
    "rhymes": rhymes_cb,
})


related_terms_templates = merge_two_dicts( common_templates, {
})

coordinate_templates = merge_two_dicts( common_templates, {
    # "coefficient",
})

#
singular_flags = [
    "singular",
    "singulière",
    "singulier"
]

plural_flags = [
    "plural",
    "plural-",
]

present_flags = [
    "present"
]

past_flags = [
    "past"
]


def is_singular(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if check_flag(t.name, singular_flags):
            return True

    # case 2
    for t in section.find_objects(Template, recursive=True):
        if t.name == "head":
            lang = t.arg(0)
            flag = t.arg(1)
            if flag == "noun plural form":
                return True

    # case 3
    for t in section.find_objects(Template, recursive=True):
        if t.name == "fi-verb form of":
            for a in t.args():
                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "c", "nodot", "suffix"):
                    continue

                v = t.arg(k)

                if v in ("1s", "2s", "3s", "s"):
                    return True

    # case 4
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("fi-form of", "conjugation of"):
            if check_flag(v, singular_flags):
                return True

    return None


def is_plural(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if check_flag(t.name, plural_flags):
            return True

    # case 2
    for t in section.find_objects(Template, recursive=True):
        if t.name == "fi-verb form of":
            for a in t.args():
                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "c", "nodot", "suffix"):
                    continue

                v = t.arg(k)

                if v in ("1p", "2p", "3p", "p", "plural"):
                    return True

    # case 3
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("fi-form of", "conjugation of"):
            v = t.arg("pl")
            if check_flag(v, plural_flags):
                return True

    return None


def is_verb_present(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if check_flag(t.name, present_flags):
            return True

    # case 2
    for t in section.find_objects(Template, recursive=True):
        if t.name == "fi-verb form of":
            for a in t.args():
                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "c", "nodot", "suffix"):
                    continue

                v = t.arg(k)

                if v in ("pres"):
                    return True

    # case 3
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("fi-form of", "conjugation of"):
            value = t.arg("tense")
            if value and value.find("present") != -1:
                return True
    return None


def is_verb_past(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if check_flag(t.name, past_flags):
            return True

    # case 2
    for t in section.find_objects(Template, recursive=True):
        if t.name == "inflection of":
            # {{inflection of|do||past|part|lang=en}}
            a3 = t.arg(2)
            if a3 == "past":
                return True

    # case 3
    for t in section.find_objects(Template, recursive=True):
        if t.name == "fi-verb form of":
            for a in t.args():
                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "c", "nodot", "suffix"):
                    continue

                v = t.arg(k)

                if v in ("past"):
                    return True

    # case 4
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("fi-form of", "conjugation of"):
            value = t.arg("tense")
            if value and value.find("past") != -1:
                return True

    return None


def is_male(section):
    # {{g}} - masculin 
    # 
    # {{m}} - masculin 
    #   {{m}} - masculin 
    #   {{m|a}} - masculin 
    #   {{m|i}} - masculin 
    #   {{m|équiv=fille}} - masculin, link to féminin "fille"
    for t in section.find_objects(Template, recursive=False):
        if t.name == "g":
            values = [a.get_value() for a in t.args()]
            return ("m" in values) or ("m-p" in values)
        elif t.name == "m":
            return True
        elif t.name == "mf":
            return True
        elif t.name == "fm":
            return True
        elif t.name in ("masculine plural past participle of", "masculine plural of"):
            return True

def is_female(section):
    # {{g}} - masculin 
    # 
    # {{f}} - masculin 
    #   {{f}} - masculin 
    #   {{f|a}} - masculin 
    #   {{f|i}} - masculin 
    for t in section.find_objects(Template, recursive=False):
        if t.name == "g":
            values = [a.get_value() for a in t.args()]
            return ("f" in values) or ("f-p" in values)
        elif t.name == "f":
            return True
        elif t.name == "mf":
            return True
        elif t.name == "fm":
            return True
        elif t.name == "deutsch substantiv übersicht":
            g = t.arg("Genus")
            if g == "f": # female
                return True



# {{fr-inv|do}}
# {{pron|do|fr}}
# {{pron|kat|fr}} 


def try_well_formed_structure(tree, label, language):
    def find_section_name_in_header_template(header):
        for t in header.find_objects(Template, recursive=True):
            name = t.name
            lang = t.arg(0)
            if name:
                lang = lang.lower() if lang else lang
                yield(lang, name)
                
    def is_lang_section_templated(sec):
        # {{langue|fr}}
        for (lang, name) in find_section_name_in_header_template(sec.header):
            if lang in languages:
                if name in lang_sections:
                    return True
            elif lang is None:
                if name in lang_sections:
                    return True
        return False

    def is_lang_section(sec):
        if sec.name in lang_sections:
            return True
        elif is_lang_section_templated(sec) :
            return True
        else:
            return False

    def find_tos_section_name_in_header_template(header):
        # {{s|nom|fr|num=1}}
        # {{Wortart|Konjugierte Form|Deutsch}}
        for t in header.find_objects(Template, recursive=True):
            name = t.arg(0)
            lang = t.arg(1)
            if name:
                name = name.lower() if name else name
                lang = lang.lower() if lang else lang
                yield(lang, name)
                
    def is_tos_section_templated(sec):
        # "{{s|nom|fr|num=1}}",
        for (lang, name) in find_tos_section_name_in_header_template(sec.header):
            if lang in languages:
                for wt, tos_section_names in tos_sections.items():
                    if name in tos_section_names:
                        return True
            elif lang is None:
                for wt, tos_section_names in tos_sections.items():
                    if name in tos_section_names:
                        return True
        return False

    def is_tos_section(sec):
        for wt, tos_section_names in tos_sections.items():
            if sec.name in tos_section_names:
                return True

        if is_tos_section_templated(sec):
            return True
        else:
            return False

    def get_word_type_templated(sec):
        # "{{s|nom|fr|num=1}}",
        for (lang, name) in find_tos_section_name_in_header_template(sec.header):
            if lang in languages:
                for wt, tos_section_names in tos_sections.items():
                    if name in tos_section_names:
                        return wt
            elif lang is None:
                for wt, tos_section_names in tos_sections.items():
                    if name in tos_section_names:
                        return wt

    def get_word_type(sec):
        for wt, tos_section_names in tos_sections.items():
            if sec.name in tos_section_names:
                return wt
        wt = get_word_type_templated(sec)
        if wt:
            return wt
        return None

    def get_singular_variant(sec):
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "en-noun":
                (s, p, is_uncountable) = en_noun(t)
                return s
            elif t.name == "fr-rég":
                s = t.arg("s")
                if s:
                    return s
            elif t.name == "fr-inv":
                s = t.arg("s")
                if s:
                    return s
        return None

    def get_plural_variant(sec):
        for t in sec.find_objects(Template, recursive=False):
            if t.name == "en-noun":
                (s, p, is_uncountable) = en_noun(t)
                if is_uncountable:
                    return None
                return p
            elif t.name == "fr-rég":
                p = t.arg("p")
                if p:
                    return p
                else:
                    p = label + "s"
                    return p
        return None

    def get_male_variant(sec):
        # case 1
        # {{F|équiv=}}
        #
        # {{Weibliche Wortformen}}
        # :[1] [[Kätzin]]
        # {{Männliche Wortformen}}
        # :[1] [[Kater]]
        #for t in sec.find_objects(Template, recursive=True):
        #    if t.name == "f":
        #        return t.arg("équiv")
                
        # case 2
        # {{Männliche Wortformen}}
        # :[1] [[Kater]]
        for subsec in sec.find_objects(Section, recursive=True):
            if subsec.has_name("männliche wortformen"):
                for link in subsec.find_objects(Link, recursive=True):
                    return link.get_text().strip()
        return None

    def get_female_variant(sec):
        # case 1
        # {{weibliche wortformen}}
        # [[...]]
        for subsec in sec.find_objects(Section, recursive=True):
            if subsec.has_name("weibliche wortformen"):
                for link in subsec.find_objects(Link, recursive=True):
                    return link.get_text().strip()
        
        # case 2
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "m":
                return t.arg("équiv")

        return None
        
    def get_examples(sec):
        pass
        
    def check_section_name(section, allowed_names):
        if section.name in allowed_names:
            return True
            
        for t in section.header.find_objects(Template):
            if t.name in allowed_names:
                return True
        return False

    def mine_helper(section, section_names, section_templates, word, word_method, allow_multilang=False, capture_links=False):
        if check_section_name(section, section_names):
            for t in section.find_objects(Template, recursive=True):
                callback = section_templates.get(t.name, None)
                if callback:
                    for lang, term in callback(t):
                        if allow_multilang or lang is None or lang in languages:
                            method_to_call = getattr(word, word_method)
                            result = method_to_call(lang, term)
                            
            if capture_links:
                for l in section.find_objects(Link, recursive=True):
                    term = l.get_text().strip()
                    method_to_call = getattr(word, word_method)
                    result = method_to_call(None, term)
    
    #
    words = []

    # flags
    is_lang_section_found = False
    is_tos_section_found = False

    # find language section
    for lang_section in tree.find_top_objects(Section, is_lang_section):
        is_lang_section_found = True
        is_tos_section_found = False

        # find type-of-speech section
        for tos_section in lang_section.find_top_objects(Section, is_tos_section):
            is_tos_section_found = True

            word = Word()
            words.append(word)
            word.LabelName = label
            word.LanguageCode = language
            word.Type = get_word_type(tos_section)

            # find value sections
            for section in tos_section.find_objects(Section, recursive=True):
                # OK. TOS section found
                # Translations
                mine_helper(section, translation_sections, translations_templates, word, "add_translation",
                            allow_multilang=True)

                # Synonymy
                mine_helper(section, synonym_sections, synonyms_templates, word, "add_synonym", capture_links=True)
                #for li in section.find_objects(Li, recursive=False):
                #    for link in li.find_objects(Link, recursive=False):
                #        word.add_synonym(None, link.get_text())

                # Conjugation
                mine_helper(section, conjugation_sections, conjugation_templates, word, "add_conjugation")

                # Antonymy
                mine_helper(section, antonymy_sections, antonymy_templates, word, "add_antonym")

                # Hypernymy
                mine_helper(section, hypernymy_sections, hypernymy_templates, word, "add_hypernym")

                # Hyponymy
                mine_helper(section, hyponymy_sections, hyponym_templates, word, "add_hyponym")

                # Meronymy
                mine_helper(section, meronymy_sections, meronymy_templates, word, "add_meronym")

                # Holonymy
                mine_helper(section, holonymy_sections, holonymy_templates, word, "add_holonym")

                # Troponymy
                mine_helper(section, troponymy_sections, troponymy_templates, word, "add_troponym")

                # Otherwise
                # {{Verkleinerungsformen}}
                # :[[...]]
                # {{Oberbegriffe}}
                # :[1] [[Haustier]], [[Säugetier]]
                # {{Unterbegriffe}}
                # :[1] ''nach Geschlecht:'' [[Kater]], [[Kätzin]]
                pass

                # AlternativeFormsOther
                mine_helper(section, alternative_forms_sections, alternative_forms_templates, word,
                            "add_alternative_form")

                # RelatedTerms
                mine_helper(section, related_sections, related_terms_templates, word, "add_related")

                # Coordinate
                mine_helper(section, coordinate_sections, coordinate_templates, word, "add_coordinate")
                
                # Examples
                # {{Beispiele}}
                # :[[...]]
                
            # verb forms
            for t in tos_section.find_objects(Template, recursive=True):
                if t.name == "deutsch verb übersicht":
                    for s in Deutsch_Verb(t):
                        word.add_alternative_form(None, s)
                elif t.name == "deutsch substantiv übersicht":
                    for s in Deutsch_Substantiv(t):
                        word.add_alternative_form(None, s)

            # IsMale        # "g|m" "g|m-p" "m"
            word.IsMale = is_male(tos_section)

            # IsFeminine    # "g|f" "g|m|f" "g|f-p" "f"
            word.IsFeminine = is_female(tos_section)

            # IsSingle
            word.IsSingle = is_singular(tos_section)

            # IsPlural
            word.IsPlural = is_plural(tos_section)

            # IsVerbPresent
            word.IsVerbPresent = is_verb_present(tos_section)

            # IsVerbPast
            word.IsVerbPast = is_verb_past(tos_section)

            # IsVerbFutur

            # SingleVariant
            word.SingleVariant = get_singular_variant(tos_section)

            # PluralVariant
            word.PluralVariant = get_plural_variant(tos_section)

            # MaleVariant
            word.MaleVariant = get_male_variant(tos_section)

            # FemaleVariant
            word.FemaleVariant = get_female_variant(tos_section)

            # Explainations
            word.Explainations = []
            # try {{Bedeutungen}} first
            for expl_section in tos_section.find_objects(Section, recursive=False):
                if expl_section.name == "bedeutungen":
                    for li in expl_section.find_objects(Li, recursive=False):
                        word.Explainations.append(li)
                    break
            else:
                # try get list in TOS section
                for li in tos_section.find_objects(Li, recursive=False):
                    word.Explainations.append(li)

            # split by explainations
            if hasattr(word, "Explainations") and word.Explainations:
                for li in word.Explainations:
                    w = word.clone()
                    w.LabelType = get_label_type(li)
                    w.add_explaniation(li.get_raw(), li.get_text().strip())
                    words.append(w)
                words.remove(word)

        break

    if not is_lang_section_found:
        log_lang_section_not_found.warn("%s", label)

    if not is_tos_section_found:
        log_tos_section_not_found.warn("%s", label)

    return words
