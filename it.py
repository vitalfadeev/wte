# !/usr/bin/python3
# !/usr/bin/python3
# -*- coding: utf-8 -*-

from wte import Word, KEYS, WORD_TYPES, get_label_type
from wikoo import Li, Template, Section, Link, String
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found
from helpers import merge_two_dicts, check_flag

# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
languages = ["it", "italian"]
lang_sections = ["italian", "-it-", "it"]
# name : name
# {{s}} : s_cb
# {{s|name}} : s_cb
# {{s|name|lang}} : s_cb
# {{langue|fr}} : langue_cb
# {{-it-}} : -it-
# {{-noun-}} : -noun-
section_name_templates = {
    's': lambda t: t.arg(0) if t.arg(1) is None or t.arg(1).lower().strip() in languages else None,
    'langue': lambda t: t.arg(0),
}

section_templates = [
    "-sost-",
    "-sill-",
    "-pron-",
    "-etim-",
    "-quote-",
    "-sin-",
    "-der-",
    "-rel-",
    "-var-",
    "-alter-",
    "-iperon-",
    "-prov-",
    "-trad-",
    "-ref-",
    "-acron-",
    "-agg form-",
    "-agg dim-",
    "-agg form-",
    "-agg num form-",
    "-agg num-",
    "-agg poss-",
    "-agg-",
    "-alter-",
    "-art-",
    "-avv-",
    "-cifr-",
    "-cod-",
    "-cong-",
    "-coni-",
    "-de-",
    "-decl-",
    "-der-",
    "-en-",
    "-es-",
    "-espr-",
    "-etim-",
    "-fal-",
    "-fr-",
    "-inter-",
    "-iperon-",
    "-ipon-",
    "-it-",
    "-lett-",
    "-loc avv-",
    "-loc nom-",
    "-nl-",
    "-noconf-",
    "-nome-",
    "-np-",
    "-ord-",
    "-pref-",
    "-prep-",
    "-pron dim-",
    "-pron form-",
    "-pron poss-",
    "-pron-",
    "-pronome-",
    "-prov-",
    "-quote-",
    "-ref-",
    "-rel-",
    "-scn-",
    "-sill-",
    "-sin-",
    "-sost  form-",
    "-sost form-",
    "-sost-",
    "-suff-",
    "-trad-",
    "-trad1-",
    "-trad2-",
    "-uso-",
    "-var-",
    "-varie lingue-",
    "-vec-",
    "-verb  form-",
    "-verb -",
    "-verb form-",
    "-verb formr-",
    "-verb-",
    "-verb  form-",
    "-verb -",
    "-verb form-",
    "-verb formr-",
    "-verb-",
]

# Type of speech sections
# Wortart - tos
# == butter ({{Sprache|Deutsch}}) ==
# === {{Wortart|Konjugierte Form|Deutsch}} ===
tos_sections = {
    WORD_TYPES.NOUN: [
        "nome",
        "-nome-",
        "-sost-",
        "-sost  form-",
        "-sost form-",

        "substantiv",

        "noun",
        "noun 1",
        "noun 2",
        "pronoun",
        "proper noun",
        "substantif",
        "nombre",
        "nom",
        "nom commun",
        "nom de famille",
        "nom propre",
    ],
    WORD_TYPES.ADJECTIVE: [
        "aggettivo",
        "-agg form-",
        "-agg dim-",
        "-agg form-",
        "-agg num form-",
        "-agg num-",
        "-agg poss-",
        "-agg-",

        "adjektiv",

        "abbreviation",
        "adjective",
        "adjetivo",
        "adjectif",
        "adjectif démonstratif",
        "adjectif indéfini",
        "adjectif numéral",
        "adjectif possessif",
        "adjectif relatif",
        "adj",
    ],
    WORD_TYPES.VERB: [
        "verbo",
        "-verb  form-",
        "-verb -",
        "-verb form-",
        "-verb formr-",
        "-verb-",

        "verb",

        "verbo",
        "verbe",
    ],
    WORD_TYPES.ADVERB: [
        "avverbio",
        "-avv-",
        "-loc avv-",

        "adverb",

        "adverb",
        "adverbe",
        "adverbe interrogatif",
        "adverbe interrogatif",
        "adv",
        "adverbio",
        "proverbe",
    ],
    WORD_TYPES.PREDICATIVE: [
        "prädikativ",

        "predicative"
    ],
    WORD_TYPES.CONJUNCTION: [
        "congiunzione",
        "-cong-",

        "konjunktion",
        "konjugierte Form",

        "conjugation",
        "conjunción",
        "conjonction",
        "conjonction de coordination",
    ],
    WORD_TYPES.PREPOSITION: [
        "preposizione",
        "-prep-",

        "präposition",

        "preposition",
        "preposición",
        "préposition",
    ],
    WORD_TYPES.PRONOUN: [
        "pronome",
        "-pron dim-",
        "-pron form-",
        "-pron poss-",
        "-pronome-",

        "pronomen",

        "pronoun",
        "pronombre",
        "pronom",
        "pronom démonstratif",
        "pronom indéfini",
        "pronom interrogatif",
        "pronom personnel",
        "pronom relatif",
        "prénom",
    ],
    WORD_TYPES.INTERJECTION: [
        "interiezione",
        "-inter-",

        "interjektion",

        "interjection",
        "interjection 1",
        "interjection 2",
        "interjección",
    ],
    WORD_TYPES.PARTICLE: [
        "particella",

        "partikel",

        "particle",
        "partícula",
        "particule",
    ],
    WORD_TYPES.ARTICLE: [
        "articolo",
        "-art-",

        "artikel",

        "article",
        "artículo",
        "article",
        "article défini",
        "article défini",
        "article indéfini",
        "article indéfini",
    ],
    WORD_TYPES.NUMERAL: [
        "-cifr-",

        "number",
        "numeral",
        "numéral",
        "onomatopée",
    ]
}

# translation sections
translation_sections = [
    "-trad-",
    "-trad1-",
    "-trad2-",
    "übersetzungen",
    "translations",

    "translations",
    "translation",
    "traductions",
]

# synonym sections
synonym_sections = [
    "-sin-",
    "sinonimi",
    "synonyme",

    "synonyms",
    "synonym",
    "synonyme",
    "synonymes",
]

# conjugation sections
conjugation_sections = [
    "conjunction",
    "-coni-",

    "conjugation",
]

# antonymy_sections
antonymy_sections = [
    "gegenwörter",
    "antonyms",
]

# hypernymy_sections
hypernymy_sections = [
    "-iperon-",
    "-sill-",
    "hypernyms",
]

# hyponymy_sections
hyponymy_sections = [
    "-ipon-",
    "hyponyms",
]

# meronymy_sections
meronymy_sections = [
    "meronyms"
]

# holonymy_sections
holonymy_sections = [
    "holonyms",
]

# troponymy_sections
troponymy_sections = [
    "troponyms",
]

# alternative_forms_sections
alternative_forms_sections = [
    "alternative forms",
    "-alter-"
    "-var-",
    "-der-",
]

# related_sections
related_sections = [
    "related terms"
    "-rel-",
]

# coordinate_sections
coordinate_sections = [
    "coordinate terms",
]


def Deutsch_Substantiv(t):
    g = t.arg("Genus")
    if g == "f":  # female
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
    result = [s.strip() for s in result if s]

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
    result = [s.strip() for s in result if s]

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
    "w": w_cb,
    # *{{w|William Shakespeare|Shakespeare}} | *{{w|William Shakespeare|Shakespeare|lang=fr}} | *{{w|lang=fr|William Shakespeare|Shakespeare}}
    "wikipedia": wikipedia_cb,  # {{wikipedia|article|link title}}
    "wikispecies": wikispecies_cb,
}

translations_templates = {
    "ü": t_cb,
    "üt": t_cb,

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
    "trad+": t_cb,
    "trad-": t_cb,
    "trad--": t_cb,
    "trad": t_cb,
}

synonyms_templates = merge_two_dicts(common_templates, {
    "s": synonym_cb,
    "syn": synonym_cb,
    "synonym of": synonym_cb,
})

antonymy_templates = merge_two_dicts(common_templates, {
})

hypernymy_templates = merge_two_dicts(common_templates, {
})

hyponym_templates = merge_two_dicts(common_templates, {
})

meronymy_templates = merge_two_dicts(common_templates, {
})

holonymy_templates = merge_two_dicts(common_templates, {
})

troponymy_templates = merge_two_dicts(common_templates, {
})

alternative_forms_templates = merge_two_dicts(common_templates, {
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

related_terms_templates = merge_two_dicts(common_templates, {
})

coordinate_templates = merge_two_dicts(common_templates, {
    # "coefficient",
})

#
singular_flags = [
    "singular",
    "singulière",
    "singulier"
]

plural_flags = [
    "plurale",
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

    # case 5: ''m sing'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''m sing''") != -1:
            return True
        if s.get_text().find("''f sing''") != -1:
            return True
            
    return None


def is_plural(section):
    # case 1: {{plural}}
    for t in section.find_objects(Template, recursive=True):
        if check_flag(t.name, plural_flags):
            return True

    # case 2: {{fi-verb form of|p=plural}}
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

    # case 3: {{fi-form of|pl=plurale}}
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("fi-form of", "conjugation of"):
            v = t.arg("pl")
            if check_flag(v, plural_flags):
                return True
                
                
    # case 4: "plurale" in explanation
    for li in section.find_objects(Li, recursive=False):
        for flag in plural_flags:
            if li.get_text().find(flag) != -1:
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

    # case 4: in explaination
    for li in section.find_objects(Li, recursive=True):
        if li.get_text().find("presente") != -1:
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

    # case 5: in explaination
    for li in section.find_objects(Li, recursive=False):
        if li.get_text().find("passato") != -1 or li.get_text().find("passata") != -1:
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

    # case 2: "maschile" in explanation
    for li in section.find_objects(Li, recursive=False):
        if li.get_text().find("maschile") != -1:
            return True

    # case 3: ''m sing'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''m sing''") != -1:
            return True
            
    # case 4: ''m pl'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''m pl''") != -1:
            return True
            
    # case 5: ''m inv'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''m inv''") != -1:
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
            if g == "f":  # female
                return True
                
    # case 2: "femminile" in explanation
    for li in section.find_objects(Li, recursive=False):
        if li.get_text().find("femminile") != -1:
            return True

    # case 3: ''f sing'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''f sing''") != -1:
            return True
            
    # case 4: ''f pl'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''f pl''") != -1:
            return True
            
    # case 5: ''f inv'' in section
    for s in section.find_objects(String, recursive=False):
        if s.get_text().find("''f inv''") != -1:
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
                yield (lang, name)

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
        elif is_lang_section_templated(sec):
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
                yield (lang, name)

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

        # case 2: {{Tabs | m = maschile singolare | mp = maschile plurale | f = femminile singolare | fp = femminile plurale }}
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "tabs":
                ms = t.arg("m")
                ms = ms if ms else t.arg(0)
                return ms

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

        # case 2: {{Tabs | m = maschile singolare | mp = maschile plurale | f = femminile singolare | fp = femminile plurale }}
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "tabs":
                mp = t.arg("mp")
                mp = mp if mp else t.arg(1)
                return mp
                
        return None

    def get_male_variant(sec):
        # case 1
        # {{F|équiv=}}
        #
        # {{Weibliche Wortformen}}
        # :[1] [[Kätzin]]
        # {{Männliche Wortformen}}
        # :[1] [[Kater]]
        # for t in sec.find_objects(Template, recursive=True):
        #    if t.name == "f":
        #        return t.arg("équiv")

        # case 2
        # {{Männliche Wortformen}}
        # :[1] [[Kater]]
        for subsec in sec.find_objects(Section, recursive=True):
            if subsec.name == "männliche wortformen":
                for link in subsec.find_objects(Link, recursive=True):
                    return link.get_text().strip()
                    
        # case 2: {{Tabs | m = maschile singolare | mp = maschile plurale | f = femminile singolare | fp = femminile plurale }}
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "tabs":
                ms = t.arg("m")
                ms = ms if ms else t.arg(0)
                return ms
                
        return None

    def get_female_variant(sec):
        # case 1
        # {{weibliche wortformen}}
        # [[...]]
        for subsec in sec.find_objects(Section, recursive=True):
            if subsec.name == "weibliche wortformen":
                for link in subsec.find_objects(Link, recursive=True):
                    return link.get_text().strip()

        # case 2
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "m":
                return t.arg("équiv")

        # case 3: {{Tabs | m = maschile singolare | mp = maschile plurale | f = femminile singolare | fp = femminile plurale }}
        for t in sec.find_objects(Template, recursive=True):
            if t.name == "tabs":
                fs = t.arg("f")
                fs = fs if fs else t.arg(2)
                return fs
        
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

    def mine_helper(section, section_names, section_templates, word, word_method, allow_multilang=False,
                    capture_links=False):
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
            for section in tos_section.find_objects(Section, recursive=False):
                # OK. TOS section found
                # Translations
                if section.name in translation_sections:
                    for li in section.find_objects(Li, recursive=False):
                        for t in li.find_objects(Template, recursive=False):
                            lang = t.name
                            for link in li.find_objects(Link, recursive=False):
                                term = link.get_text()
                                word.add_translation(lang, term)
                            break

                # Synonymy
                #mine_helper(section, synonym_sections, synonyms_templates, word, "add_synonym", capture_links=True)
                if section.name in synonym_sections:
                    for (lang, term) in section.find_terms(in_links=True, in_templates=synonyms_templates, lang_keys=["lang", 0], term_keys=[1]):
                        word.add_synonym(lang, term)

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
                # {{Tabs | m = maschile singolare | mp = maschile plurale | f = femminile singolare | fp = femminile plurale }}
                for t in tos_section.find_objects(Template, recursive=True):
                    if t.name == "tabs":
                        ms = t.arg("m")
                        ms = ms if ms else t.arg(0)
                        mp = t.arg("mp")
                        mp = mp if mp else t.arg(1)
                        fs = t.arg("f")
                        fs = fs if fs else t.arg(2)
                        fp = t.arg("fp")
                        fp = fp if fp else t.arg(3)
                        ms2 = t.arg("m2")
                        mp2 = t.arg("mp2")
                        fs2 = t.arg("m2")
                        fp2 = t.arg("mp2")
                        word.add_alternative_form(None, ms)
                        word.add_alternative_form(None, mp)
                        word.add_alternative_form(None, fs)
                        word.add_alternative_form(None, fp)
                        word.add_alternative_form(None, ms2)
                        word.add_alternative_form(None, mp2)
                        word.add_alternative_form(None, fs2)
                        word.add_alternative_form(None, fp2)
                        break

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
                if expl_section.name == "-sost-" or expl_section.name == "-uso-":
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
