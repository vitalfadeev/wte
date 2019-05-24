#!/usr/bin/python3
# -*- coding: utf-8 -*-

from wte import Word, KEYS, WORD_TYPES, get_label_type
from wikoo import Li, Template, Section, Link
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found


# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
lang_sections = ["french",  "{{-fr-}}", "{{langue|fr}}"]

word_type_sections = {
    "substantif":           WORD_TYPES.NOUN,
    "nom":                  WORD_TYPES.NOUN,
    "adjectif":             WORD_TYPES.ADJECTIVE,
    "verbe":                WORD_TYPES.VERB,
    "proverbe":             WORD_TYPES.ADVERB,
   #"предикатив":           WORD_TYPES.PREDICATIVE,
    "conjonction":          WORD_TYPES.CONJUNCTION,
    "préposition":          WORD_TYPES.PREPOSITION,
    "pronom":               WORD_TYPES.PRONOUN,
    "interjection":         WORD_TYPES.INTERJECTION,
    "particule":            WORD_TYPES.PARTICLE,
    "article":              WORD_TYPES.ARTICLE,
    "numéral":              WORD_TYPES.NUMERAL,
}


def is_singular(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if t.name.find("singular") != -1:
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
            if v.find("singular") != -1:
                return True

    return None


def is_plural(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if t.name.find("plural") != -1:
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
            if v and v.find("plural") != -1:
                return True

    return None


def is_verb_present(section):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if t.name.find("present") != -1:
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
        if t.name.find("past") != -1:
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


# Type of speech sections
tos_sections = {
    WORD_TYPES.NOUN: [
        # "abbreviation",
        # "acronym",
        # "adjective",
        # "initialism",
        "noun",
        "noun 1",
        "noun 2",
        "pronoun",
        "proper noun"
    ],
    WORD_TYPES.ADJECTIVE: [
        "abbreviation",
        "adjective",
    ],
    WORD_TYPES.VERB: [
        "verb"
    ],
    WORD_TYPES.ADVERB: [
        "adverb"
    ],
    WORD_TYPES.PREDICATIVE: [
        "predicative"
    ],
    WORD_TYPES.CONJUNCTION: [
        "conjugation"
    ],
    WORD_TYPES.PREPOSITION: [
        "preposition"
    ],
    WORD_TYPES.PRONOUN: [
        "pronoun"
    ],
    WORD_TYPES.INTERJECTION: [
        "interjection",
        "interjection 1",
        "interjection 2",
    ],
    WORD_TYPES.PARTICLE: [
        "particle"
    ],
    WORD_TYPES.ARTICLE: [
        "article"
    ],
    WORD_TYPES.NUMERAL: [
        "number",
        "numeral"
    ]
}

# translation sections
translation_sections = [
    "translations"
]

# synonym sections
synonym_sections = [
    "synonyms",
    "synonym"
]

# conjugation sections
conjugation_sections = [
    "conjugation"
]

# antonymy_sections
antonymy_sections = [
    "antonyms"
]

# hypernymy_sections
hypernymy_sections = [
    "hypernyms"
]

# hyponymy_sections
hyponymy_sections = [
    "hyponyms"
]

# meronymy_sections
meronymy_sections = [
    "meronyms"
]

# holonymy_sections
holonymy_sections = [
    "holonyms"
]

# troponymy_sections
troponymy_sections = [
    "troponyms"
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
    "coordinate terms"
]

word_type_sections = {
    "nombre": WORD_TYPES.NOUN,
    "adjetivo": WORD_TYPES.ADJECTIVE,
    "verbo": WORD_TYPES.VERB,
    "adverbio": WORD_TYPES.ADVERB,
    # "prädikativ":           WORD_TYPES.PREDICATIVE,
    "conjunción": WORD_TYPES.CONJUNCTION,
    "preposición": WORD_TYPES.PREPOSITION,
    "pronombre": WORD_TYPES.PRONOUN,
    "interjección": WORD_TYPES.INTERJECTION,
    "partícula": WORD_TYPES.PARTICLE,
    "artículo": WORD_TYPES.ARTICLE,
    # "числительное":         WORD_TYPES.NUMERAL,
}


# section rules
# section_rules = {
# "english"       : section_english_cb,
# "noun"          : section_noun_cb,
# "verb"          : section_verb_cb,
# "adj"           : section_adj_cb,
##"translingual"  : translingual_cb,
# }

# template rules
# template_rules = {
# "en-noun"   : noun_cb,
# "id-noun"   : noun_cb,
# "enm-noun"  : noun_cb,
# "fr-noun"   : noun_cb,
# "fro-noun"  : noun_cb,
# "ro-noun"   : noun_cb,
# "ga-noun"   : noun_cb,
# "gd-noun"   : noun_cb,
# "nrf-noun"  : noun_cb,
# "en-adj"    : adj_cb,
# "en-verb"   : verb_cb,
# "inh"       : inh_cb,
# "t"         : translation_cb,
# "t+"        : translation_cb,
# "t-simple"  : translation_cb,
# "syn"       : synonym_cb,
# "syn2"      : synonym_cb,
# "syn3"      : synonym_cb,
# "syn4"      : synonym_cb,
# "syn5"      : synonym_cb,
# "syn1"      : synonym_cb,
# "syn2-u"    : synonym_cb,
# "syn3-u"    : synonym_cb,
# "syn4-u"    : synonym_cb,
# "syn5-u"    : synonym_cb,
# "l"         : l_cb,
# "sense"     : sense_cb,
# "lb"        : label_cb,
# "lbl"       : label_cb,
# "label"     : label_cb,

# "alter"                     : alter_cb,
# "alternative form of"       : alter_cb,
# "alt form"                  : alter_cb,
# "alt form of"               : alter_cb,
# "alternative spelling of"   : alter_cb,
# "aspirate mutation of"      : alter_cb,
# "alternate spelling of"     : alter_cb,
# "altspelling"               : alter_cb,
# "standspell"                : alter_cb,
# "standard spelling of"      : alter_cb,
# "soft mutation of"          : alter_cb,
# "hard mutation of"          : alter_cb,
# "mixed mutation of"         : alter_cb,
# "lenition of"               : alter_cb,
# "alt form"                  : alter_cb,
# "altform"                   : alter_cb,
# "alt-form"                  : alter_cb,
# "apocopic form of"          : alter_cb,
# "altcaps"                   : alter_cb,
# "alternative name of"       : alter_cb,
# "honoraltcaps"              : alter_cb,
# "alternative capitalisation of" : alter_cb,
# "alternative capitalization of" : alter_cb,
# "alternate form of"         : alter_cb,
# "alternative case form of"  : alter_cb,
# "alt-sp"                    : alter_cb,
# "standard form of"          : alter_cb,
# "alternative typography of" : alter_cb,
# "elongated form of"         : alter_cb,
# "alternative name of"       : alter_cb,
# "uncommon spelling of"      : alter_cb,
# "combining form of"         : alter_cb,
# "caret notation of"         : alter_cb,
# "alternative term for"      : alter_cb,
# "altspell"                  : alter_cb,
# "eye dialect of"            : alter_cb,
# "eye dialect"               : alter_cb,
# "eye-dialect of"            : alter_cb,
# "pronunciation spelling"    : alter_cb,
# "pronunciation respelling of" : alter_cb,
# "pronunciation spelling of" : alter_cb,
# "obsolete spelling of"      : alter_cb,
# "obsolete form of"          : alter_cb,
# "obsolete typography of"    : alter_cb,
# "rareform"                  : alter_cb,
# "superseded spelling of"    : alter_cb,
# "former name of"            : alter_cb,
# "archaic spelling of"       : alter_cb,
# "dated spelling of"         : alter_cb,
# "archaic form of"           : alter_cb,
# "dated form of"             : alter_cb,
# "informal spelling of"      : alter_cb,
# "informal form of"          : alter_cb,
# "euphemistic form of"       : alter_cb,
# "euphemistic spelling of"   : alter_cb,
# "deliberate misspelling of" : alter_cb,
# "misconstruction of"        : alter_cb,
# "misspelling of"            : alter_cb,
# "common misspelling of"     : alter_cb,
# "nonstandard form of"       : alter_cb,
# "nonstandard spelling of"   : alter_cb,
# "rare form of"              : alter_cb,
# "rare spelling of"          : alter_cb,
# "initialism of"             : alter_cb,
# "abbreviation of"           : alter_cb,
# "short for"                 : alter_cb,
# "acronym of"                : alter_cb,
# "clipping of"               : alter_cb,
# "clip"                      : alter_cb,
# "clipping"                  : alter_cb,
# "short form of"             : alter_cb,
# "ellipsis of"               : alter_cb,
# "ellipse of"                : alter_cb,
# "short of"                  : alter_cb,
# "abbreviation"              : alter_cb,
# "abb"                       : alter_cb,
# "contraction of"            : alter_cb,

# "en-past of"                            : verb_past_cb,
# "en-simple past of"                     : verb_past_cb,
# "past of"                               : verb_past_cb,
# "past sense of"                         : verb_past_cb,
# "past tense of"                         : verb_past_cb,
# "en-simple past of"                     : verb_past_cb,
# "en-past of"                            : verb_past_cb,
# "past participle of"                    : verb_past_cb,
# "en-second-person singular past of"     : [verb_past_cb, (KEYS.SINGULAR, True)],
# "en-second person singular past of"     : [verb_past_cb, (KEYS.SINGULAR, True)],
# "second-person singular past of"        : [verb_past_cb, (KEYS.SINGULAR, True)],
# "second person singular past of"        : [verb_past_cb, (KEYS.SINGULAR, True)],

# "present participle of"                 : verb_present_cb,
# "gerund of"                             : verb_present_cb,
# "present tense of"                      : verb_present_cb,
# "present of"                            : verb_present_cb,
# "en-third-person singular of"           : verb_present_cb,
# "en-third person singular of"           : verb_present_cb,
# "en-archaic second-person singular of"  : verb_present_cb,
# "second-person singular of"             : verb_present_cb,

# "plural of"                             : plural_cb,
# "feminine plural of"                    : plural_cb,
# "masculine plural of"                   : plural_cb,
# "neuter plural of"                      : plural_cb,
# "nominative plural of"                  : plural_cb,
# "alternative plural of"                 : plural_cb,
# "plural form of"                        : plural_cb,
# "en-irregular plural of"                : plural_cb,

# "feminine singular of"                  : singular_cb,
# "masculine singular of"                 : singular_cb,
# "neuter singular of"                    : singular_cb,
# "en-third-person singular of"           : singular_cb,
# "en-third person singular of"           : singular_cb,
# "singular of"                           : singular_cb,
# "singular form of"                      : singular_cb,
# "en-archaic second-person singular of"  : singular_cb,
# "second-person singular of"             : singular_cb,
# "en-second-person singular past of"     : singular_cb,
# "en-second person singular past of"     : singular_cb,
# "second-person singular past of"        : singular_cb,
# "second person singular past of"        : singular_cb,
# "en-archaic third-person singular of"   : singular_cb,

# "fi-verb form of"  : fi_verb_form_of_cb,
# "fi-form of"       : fi_form_of_cb,
# "conjugation of"   : fi_form_of_cb,
# }


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


translations_templates = {
    "t": t_cb,
    "t*": t_cb,
    "t+": t_cb,
    "t+check": t_cb,
    "t+tt": t_cb,
    "t-check": t_cb,
    "t-check-egy": t_cb,
    "t-egy": t_cb,
    "t-f": t_cb,
    "t-image": t_cb,
    "t-needed": t_cb,
    "t-sile": t_cb,
    "t-simple": t_cb,
    "t-tpi": t_cb,
}

synonyms_templates = {
    "l": l_cb,
    "label": l_cb,
    "lb": lb_cb,
    "s": synonym_cb,
    "syn": synonym_cb,
    "synonym of": synonym_cb,
}

antonymy_templates = {
    "L": L_cb,  # {{l|en|[[God]] be [[with]] [[you]]}} | {{l|en|go|went}} | {{l|cs|háček}}
    "jump": jump_cb,  # {{jump|fr|combover|s|a}}
    "l": l_cb,  # {{l|cs|háček}} | {{l|en|go|went}} - word go section #went
    "lb": lb_cb,  # {{label|en|foobarbazbip}}
    "m": m_cb,  # {{m|en|word}}
    "soplink": soplink_cb,  # {{soplink|foo|/|bar|baz|-} → foo/bar baz-
    "w": w_cb,
    # *{{w|William Shakespeare|Shakespeare}} | *{{w|William Shakespeare|Shakespeare|lang=fr}} | *{{w|lang=fr|William Shakespeare|Shakespeare}}
    "wikipedia": wikipedia_cb  # {{wikipedia|article|link title}}
}


def word_Hypernyms_cb(t):
    term = t.name.split(" ")[0]
    yield (None, term)


hypernymy_templates = {
    "l": l_cb,
    "lb": lb_cb,
    "m": m_cb,
    "pedia": pedia_cb,
    "w": w_cb,
    "wikipedia": wikipedia_cb,
    "wikispecies": wikispecies_cb
}

hyponym_templates = {
    "l": l_cb,
    "lb": lb_cb,
    "m": m_cb,
    "pedia": pedia_cb,
    "w": w_cb,
    "wikipedia": wikipedia_cb,
    "wikispecies": wikispecies_cb
}

meronymy_templates = {
    "l": l_cb,
    "m": m_cb,
}

holonymy_templates = {
    "l": l_cb,
    "lb": lb_cb,
}

troponymy_templates = {
    "l": l_cb,
}


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


alternative_forms_templates = {
    "alter": alter_cb,
    "alternative form of": alternative_form_of_cb,
    "cog": cog_cb,
    # "en-adj"    : en_adj_cb,
    "en-conj": en_conj_cb,
    # "fi-alt-personal",
    "form of": form_of_cb,  # {{form of|en|alternative form|word}}
    "given name": given_name_cb,  # {{given name|en|male}}.
    "head": head_cb,
    "l": l_cb,
    "label": l_cb,
    "lb": lb_cb,
    "link": l_cb,
    "m": m_cb,
    "m-self": l_cb,
    "pedlink": pedlink_cb,
    "rhymes": rhymes_cb,
    "w": w_cb,
    "wikipedia": wikipedia_cb,
    "wikispecies": wikispecies_cb,
}


def rootsee_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    yield (lang, term)


related_terms_templates = {
    "cog": cog_cb,
    "l": l_cb,
    "lb": lb_cb,
    "link": l_cb,
    "m": m_cb,
    "pedia": pedia_cb,
    "rootsee": rootsee_cb,
    "w": w_cb,
    "wikipedia": wikipedia_cb,
    "wikispecies": wikispecies_cb,
}

coordinate_templates = {
    # "coefficient",
    "jump": jump_cb,
    "l": l_cb,
    "l-self": l_cb,
    "lb": lb_cb,
    "m": m_cb,
    "w": w_cb,
    "wikipedia": wikipedia_cb,
}


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


def try_well_formed_structure(tree, label):
    def is_lang_section(sec):
        return True if sec.name in lang_sections else False

    def is_tos_section(sec):
        for wt, tos_section_names in tos_sections.items():
            if sec.name in tos_section_names:
                return True
        return False

    def get_word_type(sec):
        for wt, tos_section_names in tos_sections.items():
            if sec.name in tos_section_names:
                return wt
        return None

    def get_singular_variant(sec):
        for t in section.find_objects(Template, recursive=True):
            if t.name == "en-noun":
                (s, p, is_uncountable) = en_noun(t)
                return s
        return None

    def get_plural_variant(sec):
        for t in section.find_objects(Template, recursive=True):
            if t.name == "en-noun":
                (s, p, is_uncountable) = en_noun(t)
                if is_uncountable:
                    return None
                return p
        return None

    def get_male_variant(sec):
        for t in section.find_objects(Template, recursive=True):
            if t.name in ("masculine plural past participle of", "masculine plural of"):
                return True
        return None

    def mine_helper(section, section_names, section_templates, word, word_method, allow_multilang=False):
        if section.name in section_names:
            for t in section.find_objects(Template, recursive=True):
                callback = section_templates.get(t.name, None)
                if callback:
                    for lang, term in callback(t):
                        if allow_multilang or lang is None or lang == "en":
                            method_to_call = getattr(word, word_method)
                            result = method_to_call(lang, term)

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
            word.LanguageCode = "en"
            word.Type = get_word_type(tos_section)

            # find value sections
            for section in tos_section.find_objects(Section, recursive=True):
                # OK. TOS section found
                # Translations
                mine_helper(section, translation_sections, translations_templates, word, "add_translation",
                            allow_multilang=True)

                # Synonymy
                mine_helper(section, synonym_sections, synonyms_templates, word, "add_synonym")

                # Conjugation
                mine_helper(section, conjugation_sections, conjugation_templates, word, "add_conjugation")

                # Antonymy
                mine_helper(section, antonymy_sections, antonymy_templates, word, "add_antonym")

                # Hypernymy
                if section.name in hypernymy_sections:
                    for t in section.find_objects(Template, recursive=True):
                        if t.name.find("Hypernyms") != -1:
                            term = t.name.split(" ")[0]
                            word.add_hypernym(None, term)

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
                pass

                # AlternativeFormsOther
                mine_helper(section, alternative_forms_sections, alternative_forms_templates, word,
                            "add_alternative_form")

                # RelatedTerms
                mine_helper(section, related_sections, related_terms_templates, word, "add_related")

                # Coordinate
                mine_helper(section, coordinate_sections, coordinate_templates, word, "add_coordinate")

                # IsMale        # "g|m" "g|m-p"
                for t in section.find_objects(Template, recursive=True):
                    if t.name == "g":
                        values = [a.get_value() for a in t.args()]
                        word.IsMale = ("m" in values) or ("m-p" in values)
                        break
                    elif t.name in ("masculine plural past participle of", "masculine plural of"):
                        word.IsMale = True
                        break

                # IsFeminine    # "g|f" "g|m|f" "g|f-p"
                for t in section.find_objects(Template, recursive=True):
                    if t.name == "g":
                        values = [a.get_value() for a in t.args()]
                        word.IsMale = ("f" in values) or ("f-p" in values)
                        break

                # IsSingle
                word.IsSingle = is_singular(section)

                # IsPlural
                word.IsPlural = is_plural(section)

                # IsVerbPresent
                word.IsVerbPresent = is_verb_present(section)

                # IsVerbPast
                word.IsVerbPast = is_verb_past(section)

                # IsVerbFutur

                # SingleVariant
                word.SingleVariant = get_singular_variant(section)

                # PluralVariant
                word.PluralVariant = get_plural_variant(section)

                # MaleVariant
                word.MaleVariant = get_male_variant(section)

                # FemaleVariant
                pass

            # Explainations
            word.Explainations = []
            for li in tos_section.find_objects(Li, recursive=False):
                word.Explainations.append(li)

            # split by explainations
            if hasattr(word, "Explainations") and word.Explainations:
                for li in word.Explainations:
                    w = word.clone()
                    w.LabelType = get_label_type(li)
                    w.add_explaniation(li.get_raw(), li.get_text())
                    words.append(w)
                words.remove(word)

        break

    if not is_lang_section_found:
        log_lang_section_not_found.warning("%s", label)

    if not is_tos_section_found:
        log_tos_section_not_found.warning("%s", label)

    return words
