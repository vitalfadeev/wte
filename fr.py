from wte import Word, WORD_TYPES
from helpers import create_storage, put_contents, get_contents, sanitize_filename, unique
from wikoo import get_label_type
from wikoo import Li, Template
import templates


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


def get_translations(section, label, text):
    """
    Find translations in section 'section'

    out: {en:[..], de:[...]}
    """
    result = []

    # case 1
    # =====Translations=====
    # {{trans-top|members of the species ''Equus ferus''}}
    # * ...
    # {{trans-bottom}}
    #for obj in section.find_objects_between_templates(Li, "trans-top", "trans-bottom"):
    #    if isinstance(obj, Li):
    #        for t in obj.find_objects(Template):
    for t in section.find_objects(Template, recursive=True):
                # {{t-simple|za|max|langname=Zhuang}}
                if t.name == "t-simple":
                    lang = t.arg(1, text)
                    term = t.arg(2, text)

                    if term:
                        result.append((lang, term))

                elif t.name.lower() == "t+":
                    # {{t+|zu|ihhashi|c5|c6}}
                    lang = t.arg(1, text)
                    term = t.arg(2, text)

                    if term:
                        result.append((lang, term))

                elif t.name.lower() == "t":
                    # {{t|ude|муи }}
                    lang = t.arg(1, text)
                    term = t.arg(2, text)

                    if term:
                        result.append((lang, term))

    # case 2
    # * {{t|en|cat}}
    """
    for t in section.find_templates_in_parents():
        # {{t-simple|za|max|langname=Zhuang}}
        if t.name.lower() == "t-simple":
            lang = t.arg(0)
            term = t.arg(1)

            if term:
                result.append((lang, term))

        elif t.name.lower() == "t+":
            # {{t+|zu|ihhashi|c5|c6}}
            lang = t.arg(0)
            term = t.arg(1)

            if term:
                result.append((lang, term))

        elif t.name.lower() == "t":
            # {{t|ude|муи }}
            lang = t.arg(0)
            term = t.arg(1)

            if term:
                result.append((lang, term))
    """

    #
    bylang = {}

    for lang, term in result:
        cln = term.replace("[", "").replace("]", "")

        if lang in bylang:
            bylang[lang].append(cln)
        else:
            bylang[lang] = []
            bylang[lang].append(cln)

    for k,v in bylang.items():
        bylang[k] = unique(v)

    return bylang


def get_conjugations(section, label, text):
    """
    Find conjugations in section 'section'
    It find templates like the {{en-conj}}, {{en-verb}} and analize its.

    out: [...]
    out: None
    """

    """
    ==English==
    ===Etymology 1===
    ====Verb====
    =====Conjugation=====
    {{en-conj|do|did|done|doing|does}}

    In: section Verb

    Out:
        [ basic, simple_past, past_participle, present_participle, simple_present_third_person ]
    """

    result = []

    # here is section ====Verb====
    for t in section.find_objects(Template, recursive=True):
        if t.name == "en-conj":
            result += templates.en_conj(t, label, text)

        elif t.name == "en-verb":
            (third, present_participle, simple_past, past_participle) = templates.en_verb(t, label, text)
            result.append(third)
            result.append(present_participle)
            result.append(simple_past)
            result.append(past_participle)

    # unique
    result = unique(result)

    return result if result else None


def is_male_variant(section, label, text):
    """
    Detect for thw word is male varant.
    Take section 'section' as argument.
    Find templates like the {{ang-noun}} and analize its.

    out: True | False
    """
    # From {{inh|en|enm|cat}}, {{m|enm|catte}},
    # from {{inh|en|ang|catt||male cat}}, {{m|ang|catte||female cat}},
    # from {{inh|en|gem-pro|*kattuz}}.
    for t in section.find_objects(Template, recursive=True):
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label, text)

            if gender == "m":
                return True

    return None

def is_female_variant(section, label, text):
    # From {{inh|en|enm|cat}}, {{m|enm|catte}},
    # from {{inh|en|ang|catt||male cat}}, {{m|ang|catte||female cat}},
    # from {{inh|en|gem-pro|*kattuz}}.
    for t in section.find_objects(Template, recursive=True):
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label, text)

            if gender == "f":
                return True

    return None


def is_singular(section, label, text):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if t.name == "en-noun" and False: # disabled
            # case 1
            (s, p, is_uncountable) = templates.en_noun(t, label, text)

            if p:
                return True

        elif t.name == "head":
            # case 2
            lang = t.arg(1, text)
            flag = t.arg(2, text)
            if flag == "noun plural form":
                return True

        elif t.name in ("feminine singular of", "masculine singular of", "neuter singular of",
                        "en-third-person singular of", "en-third person singular of",
                        "singular of", "singular form of",
                        "en-archaic second-person singular of",
                        "second-person singular of",
                        "en-second-person singular past of",
                        "en-second person singular past of",
                        "second-person singular past of",
                        "second person singular past of",
                        "en-archaic third-person singular of"
                        ):
            # case 3
            return True

        elif t.name == "fi-verb form of":
            mapping = {"1s": ["1", "singular"],
                       "2s": ["2", "singular"],
                       "3s": ["3", "singular"],
                       "1p": ["1", "plural"],
                       "2p": ["2", "plural"],
                       "3p": ["3", "plural"],
                       "p": ["plural"],
                       "plural": ["plural"],
                       "s": ["singular"],
                       "pass": ["passive"],
                       "cond": ["conditional"],
                       "potn": ["potential"],
                       "impr": ["imperative"],
                       "pres": ["present"],
                       "past": ["past"]}
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

        elif t.name in ("fi-form of", "conjugation of"):
            # case 4
            for a in t.args():
                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "2", "3", "suffix", "suffix2", "suffix3",
                         "c", "n", "type", "lang"):
                    continue

                v = t.arg(k, text)

                if not v or v == "-":
                    continue

                if v in ("first-person", "first person", "1p"):
                    v = "1"
                elif v in ("second-person", "second person", "2p"):
                    v = "2"
                elif v in ("third-person", "third person", "3p"):
                    v = "3"
                elif v == "connegative present":
                    v = "present connegative"
                elif v in ("singural", "s"):
                    v = "singular"
                elif v in ("p,"):
                    v = "plural"
                elif v == "pres":
                    v = "present"
                elif v == "imperfect":
                    v = "past"
                if k != "case":
                    if v not in ("1", "2", "3", "impersonal",
                                 "first-person singular",
                                 "first-person plural",
                                 "second-person singular",
                                 "second-person plural",
                                 "third-person singular",
                                 "third-person plural",
                                 "first, second, and third person",
                                 "singular or plural",
                                 "plural", "singular", "present", "past",
                                 "imperative", "present connegative",
                                 "indicative connegative",
                                 "indicative present",
                                 "indicative past",
                                 "potential present",
                                 "conditional present",
                                 "potential present connegative",
                                 "connegative", "partitive", "optative",
                                 "eventive",
                                 "singular and plural", "passive",
                                 "indicative", "conditional", "potential"):
                        #print(word, "FI-FORM UNRECOGNIZED", v, str(t))
                        pass

                if v in ("singular and plural", "singular or plural"):
                    return True
                elif v == "first-person singular":
                    return True
                elif v == "second-person singular":
                    return True
                elif v == "third-person singular":
                    return True

    return None


def is_plural(section, label, text):
    # {{plural of|cat|lang=en}}
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("plural of", "feminine plural of",
                      "masculine plural of",
                      "neuter plural of",
                      "nominative plural of",
                      "alternative plural of",
                      "plural form of",
                      "en-irregular plural of",
                      ):
            # case 1
            return True

        elif t.name == "fi-verb form of":
            mapping = {"1s": ["1", "singular"],
                       "2s": ["2", "singular"],
                       "3s": ["3", "singular"],
                       "1p": ["1", "plural"],
                       "2p": ["2", "plural"],
                       "3p": ["3", "plural"],
                       "p": ["plural"],
                       "plural": ["plural"],
                       "s": ["singular"],
                       "pass": ["passive"],
                       "cond": ["conditional"],
                       "potn": ["potential"],
                       "impr": ["imperative"],
                       "pres": ["present"],
                       "past": ["past"]}
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

        elif t.name in ("fi-form of", "conjugation of"):
            # case 3
            for a in t.args():

                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "2", "3", "suffix", "suffix2", "suffix3",
                         "c", "n", "type", "lang"):
                    continue

                v = t.arg(k, text)

                if not v or v == "-":
                    continue

                if v in ("first-person", "first person", "1p"):
                    v = "1"
                elif v in ("second-person", "second person", "2p"):
                    v = "2"
                elif v in ("third-person", "third person", "3p"):
                    v = "3"
                elif v == "connegative present":
                    v = "present connegative"
                elif v in ("singural", "s"):
                    v = "singular"
                elif v in ("p,"):
                    v = "plural"
                elif v == "pres":
                    v = "present"
                elif v == "imperfect":
                    v = "past"
                if k != "case":
                    if v not in ("1", "2", "3", "impersonal",
                                 "first-person singular",
                                 "first-person plural",
                                 "second-person singular",
                                 "second-person plural",
                                 "third-person singular",
                                 "third-person plural",
                                 "first, second, and third person",
                                 "singular or plural",
                                 "plural", "singular", "present", "past",
                                 "imperative", "present connegative",
                                 "indicative connegative",
                                 "indicative present",
                                 "indicative past",
                                 "potential present",
                                 "conditional present",
                                 "potential present connegative",
                                 "connegative", "partitive", "optative",
                                 "eventive",
                                 "singular and plural", "passive",
                                 "indicative", "conditional", "potential"):
                        #print(word, "FI-FORM UNRECOGNIZED", v, str(t))
                        pass
                if v in ("singular and plural", "singular or plural"):
                    return True
                elif v == "first-person plural":
                    return True
                elif v == "second-person plural":
                    return True
                elif v == "third-person plural":
                    return True

    return None


def is_verb_present(section, label, text):
    # {{present participle of}}
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("present participle of", "gerund of",
                      "present tense of", "present of",
                      "en-third-person singular of",
                      "en-third person singular of",
                      "en-archaic second-person singular of",
                      "second-person singular of",
                      ):
            return True

        elif t.name == "fi-verb form of":
            mapping = {"1s": ["1", "singular"],
                       "2s": ["2", "singular"],
                       "3s": ["3", "singular"],
                       "1p": ["1", "plural"],
                       "2p": ["2", "plural"],
                       "3p": ["3", "plural"],
                       "p": ["plural"],
                       "plural": ["plural"],
                       "s": ["singular"],
                       "pass": ["passive"],
                       "cond": ["conditional"],
                       "potn": ["potential"],
                       "impr": ["imperative"],
                       "pres": ["present"],
                       "past": ["past"]}
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

        elif t.name in ("fi-form of", "conjugation of"):
            # case 3
            for a in t.args():

                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "2", "3", "suffix", "suffix2", "suffix3",
                         "c", "n", "type", "lang"):
                    continue

                v = t.arg(k, text)

                if not v or v == "-":
                    continue

                if v in ("first-person", "first person", "1p"):
                    v = "1"
                elif v in ("second-person", "second person", "2p"):
                    v = "2"
                elif v in ("third-person", "third person", "3p"):
                    v = "3"
                elif v == "connegative present":
                    v = "present connegative"
                elif v in ("singural", "s"):
                    v = "singular"
                elif v in ("p,"):
                    v = "plural"
                elif v == "pres":
                    v = "present"
                elif v == "imperfect":
                    v = "past"
                if k != "case":
                    if v not in ("1", "2", "3", "impersonal",
                                 "first-person singular",
                                 "first-person plural",
                                 "second-person singular",
                                 "second-person plural",
                                 "third-person singular",
                                 "third-person plural",
                                 "first, second, and third person",
                                 "singular or plural",
                                 "plural", "singular", "present", "past",
                                 "imperative", "present connegative",
                                 "indicative connegative",
                                 "indicative present",
                                 "indicative past",
                                 "potential present",
                                 "conditional present",
                                 "potential present connegative",
                                 "connegative", "partitive", "optative",
                                 "eventive",
                                 "singular and plural", "passive",
                                 "indicative", "conditional", "potential"):
                        #print(word, "FI-FORM UNRECOGNIZED", v, str(t))
                        pass
                if v in ("pres", "connegative present",
                         "potential present connegative",
                         "potential present",
                         "conditional present",
                         "indicative present"):
                    return True



    return None


def is_verb_past(section, label, text):
    # {{en-past of}}
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("en-past of", "en-simple past of",
                      "past of", "past sense of",
                      "past tense of",
                      "en-simple past of", "en-past of",
                      "past participle of",
                      "en-second-person singular past of",
                      "en-second person singular past of",
                      "second-person singular past of",
                      "second person singular past of",
                      ):
            return True

        elif t.name == "inflection of":
            # {{inflection of|do||past|part|lang=en}}
            a3 = t.arg(3, text)
            if a3 == "past":
                return True

        elif t.name == "fi-verb form of":
            mapping = {"1s": ["1", "singular"],
                       "2s": ["2", "singular"],
                       "3s": ["3", "singular"],
                       "1p": ["1", "plural"],
                       "2p": ["2", "plural"],
                       "3p": ["3", "plural"],
                       "p": ["plural"],
                       "plural": ["plural"],
                       "s": ["singular"],
                       "pass": ["passive"],
                       "cond": ["conditional"],
                       "potn": ["potential"],
                       "impr": ["imperative"],
                       "pres": ["present"],
                       "past": ["past"]}
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

        elif t.name in ("fi-form of", "conjugation of"):
            # case 3
            for a in t.args():

                k = a.get_name()

                if k is None:
                    continue

                k = k.name.strip()

                if k in ("1", "2", "3", "suffix", "suffix2", "suffix3",
                         "c", "n", "type", "lang"):
                    continue

                v = t.arg(k, text)

                if not v or v == "-":
                    continue

                if v in ("first-person", "first person", "1p"):
                    v = "1"
                elif v in ("second-person", "second person", "2p"):
                    v = "2"
                elif v in ("third-person", "third person", "3p"):
                    v = "3"
                elif v == "connegative present":
                    v = "present connegative"
                elif v in ("singural", "s"):
                    v = "singular"
                elif v in ("p,"):
                    v = "plural"
                elif v == "pres":
                    v = "present"
                elif v == "imperfect":
                    v = "past"
                if k != "case":
                    if v not in ("1", "2", "3", "impersonal",
                                 "first-person singular",
                                 "first-person plural",
                                 "second-person singular",
                                 "second-person plural",
                                 "third-person singular",
                                 "third-person plural",
                                 "first, second, and third person",
                                 "singular or plural",
                                 "plural", "singular", "present", "past",
                                 "imperative", "present connegative",
                                 "indicative connegative",
                                 "indicative present",
                                 "indicative past",
                                 "potential present",
                                 "conditional present",
                                 "potential present connegative",
                                 "connegative", "partitive", "optative",
                                 "eventive",
                                 "singular and plural", "passive",
                                 "indicative", "conditional", "potential"):
                        #print(word, "FI-FORM UNRECOGNIZED", v, str(t))
                        pass
                if v in ("past", "indicative past"):
                    return True

    return None


def is_verb_futur(section, label, text):
    return None


def get_singular_variant(section, label, text):
    return None


def get_plural_variant(section, label, text):
    for t in section.find_objects(Template, recursive=True):
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label, text)

            if plural is not None:
                return unique(plural)

        elif t.name == "en-noun":
            (single, plural, is_uncountable) = templates.en_noun(t, label, text)

            if plural:
                return unique(plural)

    return None


def get_alternatives(section, label, text):
    """
    Find alternatives in section 'section'

    out: {en:[..], de:[...]}
    """
    # ==English== section here
    # ===Alternative forms===
    # * {{l|en|hower}} {{qualifier|obsolete}}

    result = []

    for sec in section.find_section("alternative forms", recursive=True):
        for t in sec.find_objects(Template, recursive=True):
            # * {{l|en|hower}}
            if t.name == "l":
                lang = t.arg(1, text)
                term = t.arg(2, text)

                if term:
                    result.append((lang, term))

    for t in section.find_objects(Template, recursive=True):
        if t.name in ("alternative form of", "alt form", "alt form of",
                      "alternative spelling of", "aspirate mutation of",
                      "alternate spelling of", "altspelling", "standspell",
                      "standard spelling of", "soft mutation of",
                      "hard mutation of", "mixed mutation of", "lenition of",
                      "alt form", "altform", "alt-form",
                      "apocopic form of", "altcaps",
                      "alternative name of", "honoraltcaps",
                      "alternative capitalisation of",
                      "alternative capitalization of", "alternate form of",
                      "alternative case form of", "alt-sp",
                      "standard form of", "alternative typography of",
                      "elongated form of", "alternative name of",
                      "uncommon spelling of",
                      "combining form of",
                      "caret notation of",
                      "alternative term for", "altspell",

                      "eye dialect of", "eye dialect", "eye-dialect of",
                      "pronunciation spelling",
                      "pronunciation respelling of",
                      "pronunciation spelling of",

                      "obsolete spelling of", "obsolete form of",
                      "obsolete typography of", "rareform",
                      "superseded spelling of", "former name of",
                      "archaic spelling of", "dated spelling of",
                      "archaic form of", "dated form of",

                      "informal spelling of", "informal form of",

                      "euphemistic form of", "euphemistic spelling of",

                      "deliberate misspelling of", "misconstruction of",
                      "misspelling of", "common misspelling of",
                      "nonstandard form of", "nonstandard spelling of",

                      "rare form of", "rare spelling of",

                      "initialism of", "abbreviation of", "short for",
                      "acronym of", "clipping of", "clip", "clipping",
                      "short form of", "ellipsis of", "ellipse of",
                      "short of", "abbreviation", "abb", "contraction of"):
            lang = t.arg(1, text)
            term = t.arg(2, text)

            if term:
                result.append((lang, term))

    #
    result = [ term for (lang, term) in result if lang == "en" or lang is None ]

    return result if result else None


def get_related(section, label, text):
    """
    Find related terms in section 'section'

    out: {en:[..], de:[...]}
    """
    # print(dir(t))
    # {{rel-top|related terms}}
    #   * {{l|en|knight}}
    #
    # {{rel-top|related terms}}
    # * {{l|en|knight}}

    # s = "{{rel-top|related terms}}"
    # lst = self.get_list_after_string(parsed, s)

    result = []

    found = False
    pos = 0

    # case 1
    # {{rel-top|related terms}}
    # * {{l|en|knight}}, {{l|en|cavalier}}, {{l|en|cavalry}}, {{l|en|chivalry}}
    # * {{l|en|equid}}, {{l|en|equine}}
    # * {{l|en|gee}}, {{l|en|haw}}, {{l|en|giddy-up}}, {{l|en|whoa}}
    # * {{l|en|hoof}}, {{l|en|mane}}, {{l|en|tail}}, {{l|en|withers}}
    # {{rel-bottom}}

    # get next list
    # get templates {{l|...}}

    generator = section.find_objects((Template, Li), recursive=True)
    for obj in generator:
        if isinstance(obj, Template) and obj.name == "rel-top":
            # OK. start
            for obj in generator:
                if isinstance(obj, Template) and obj.name == "rel-bottom":
                    break
                else:
                    if isinstance(obj, Li):
                        for t in obj.find_objects(Template):
                            if t.name == "l":
                                lang = t.arg(1, text)
                                term = t.arg(2, text)

                                if term:
                                    result.append((lang, term))
            break

    # case 2
    # {{rel-top|related terms}}
    for sec in section.find_section("related terms", recursive=True):
        for t in sec.find_objects(Template, recursive=True):
            # * {{l|en|hower}}
            if t.name == "l":
                lang = t.arg(1, text)
                term = t.arg(2, text)

                if term:
                    result.append((lang, term))

    # case 3
    # {{en-simple past of|do}}
    for t in section.find_objects(Template, recursive=True):
        # * {{l|en|hower}}
        if t.name == "en-simple past of":
            lang = t.arg("lang", text)
            term = t.arg(1, text)

            if term:
                result.append((lang, term))

        elif t.name == "present participle of":
            # {{present participle of|do}}
            lang = t.arg("lang", text)
            term = t.arg(1, text)

            if term:
                result.append((lang, term))

        elif t.name == "en-third-person singular of":
            # {{en-third-person singular of|do}}
            lang = t.arg("lang", text)
            term = t.arg(1, text)

            if term:
                result.append((lang, term))

        elif t.name == "inflection of":
            # {{inflection of|do||past|part|lang=en}}
            lang = t.arg("lang", text)
            term = t.arg(1, text)

            if term:
                result.append((lang, term))

    # case 4
    # get from parents
    """
    for t in section.find_templates_in_parents():
        if t.name == "m":
            # {{m|en|doe|t=female deer}}
            lang = t.arg(1, text)
            term = t.arg(2, text)

            if term:
                result.append((lang, term))

    """

    #
    bylang = {}

    #
    for lang, term in result:
        if lang in bylang:
            bylang[lang].append(term)
        else:
            bylang[lang] = []
            bylang[lang].append(term)

    for k,v in bylang.items():
        bylang[k] = unique(v)

    result = unique( bylang.get("en", []) + bylang.get(None, []) )

    return result if result else None


def get_synonyms(section, label, text):
    """
    Find synonyms in section 'section'

    out: {en:[..], de:[...]}
    """

    """
    ==English==
    ===Etymology 1===
    ====Noun====
    =====Synonyms=====
    * {{sense|animal}} {{l|en|horsie}}, {{l|en|nag}}, {{l|en|steed}}, {{l|en|prad}}
    * {{sense|gymnastic equipment}} {{l|en|pommel horse}}, {{l|en|vaulting horse}}
    * {{sense|chess piece}} {{l|en|knight}}
    * {{sense|illegitimate study aid}} {{l|en|dobbin}}, {{l|en|pony}}, {{l|en|trot}}

    ====Synonyms====
    * {{sense|period of sixty minutes|a season or moment}} {{l|en|stound}} {{qualifier|obsolete}}
    """

    result = []

    # here is section like a ====Noun==== or ====Verb====
    # find section =====Synonyms=====
    for sec in section.find_section("synonyms", recursive=True):
        for t in sec.find_objects(Template, recursive=True):
            # find {{sense|animal}} | {{l|en|horsie}}
            # remove brackets like a [[...]]
            # remove templates
            # get example
            if 0 and t.name == "sense":  # disabled, because words only
                lang = t.arg(1, text)
                term = t.arg(2, text)

                if term:
                    result.append((lang, term))

            elif t.name == "l":
                lang = t.arg(1, text)
                term = t.arg(2, text)

                if term:
                    result.append((lang, term))

    # case 2

    for t in section.find_objects(Template, recursive=True):
        if t.name in ("syn", "syn2", "syn3", "syn4", "syn5", "syn1",
                          "syn2-u", "syn3-u", "syn4-u", "syn5-u"):
            lang = t.arg("lang", text)
            for a in t.args():
                result.append(  (lang, a.get_value(text) ) )

    # filter "en"
    result = [ term for (lang, term) in result if lang == "en" or lang is None ]
    result = unique(result)

    return result if result else None


def get_words(article, label, text):
    lang = "fr"

    # mine info
    words = []

    # word for each type: verb, noun, enverb
    # word for each explaination

    # for each lang title
    for lang_title in lang_sections:

        # find lang
        for lang_section in article.find_section(lang_title, recursive=True):

            # for each type
            for (wt_title, wt_id) in word_type_sections.items():

                # find type sections
                for wt_section in lang_section.find_section(wt_title, recursive=True):

                    def create_word():
                        word = Word()
                        word.LabelName              = label
                        word.LabelType              = get_label_type(expl, text)
                        word.LanguageCode           = lang
                        word.Type                   = wt_id
                        word.Explaination           = expl.get_raw(text).replace("\n", "\\n")
                        word.ExplainationExamples   = None
                        word.IsMaleVariant          = is_male_variant(wt_section, label, text)
                        word.IsFemaleVariant        = is_female_variant(wt_section, label, text)
                        word.MaleVariant            = None
                        word.FemaleVariant          = None
                        word.IsSingleVariant        = is_singular(wt_section, label, text)
                        word.IsPluralVariant        = is_plural(wt_section, label, text)
                        word.SingleVariant          = get_singular_variant(wt_section, label, text)
                        word.PluralVariant          = get_plural_variant(wt_section, label, text)
                        word.AlternativeFormsOther  = get_alternatives(wt_section, label, text)
                        word.RelatedTerms           = get_related(wt_section, label, text)
                        word.IsVerbPast             = is_verb_present(wt_section, label, text)
                        word.IsVerbPresent          = is_verb_past(wt_section, label, text)
                        word.IsVerbFutur            = is_verb_futur(wt_section, label, text)
                        word.Conjugation            = get_conjugations(wt_section, label, text)
                        word.Synonyms               = get_synonyms(wt_section, label, text)
                        translations                = get_translations(wt_section, label, text)
                        word.Translation_EN         = translations.get("en", None)
                        word.Translation_FR         = translations.get("fr", None)
                        word.Translation_DE         = translations.get("de", None)
                        word.Translation_IT         = translations.get("it", None)
                        word.Translation_ES         = translations.get("es", None)
                        word.Translation_RU         = translations.get("ru", None)
                        word.Translation_PT         = translations.get("pt", None)

                        return word

                    # find explainations
                    is_expl_found = False

                    for expl in wt_section.get_explainations():
                        is_expl_found = True
                        yield create_word()

                    if not is_expl_found:
                        expl = Li(-1, 0)
                        # just word, without explaination
                        #assert 0, "no explaination"
                        yield create_word()

