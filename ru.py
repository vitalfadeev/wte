from wte import Word, WORD_TYPES
from helpers import create_storage, put_contents, get_contents, sanitize_filename, unique, get_number
from wikoo import Li, Template, Link, Section
from loggers import log
import templates


# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
lang_sections = ["russian", "{{-ru-}}", "{{langue|ru}}", "ru", "русский"]

msections = ["морфологические и синтаксические свойства"]
# "Семантические свойства"

word_type_sections = {
    "сущ":                  WORD_TYPES.NOUN,
    "существительное":      WORD_TYPES.NOUN,
    "сущ ru":               WORD_TYPES.NOUN,
    "сущ ru f ina 8a":      WORD_TYPES.NOUN,
    "сущ ru f ina 3d":      WORD_TYPES.NOUN,
    "сущ ru f ina 3f":      WORD_TYPES.NOUN,
    "глагол":               WORD_TYPES.VERB,
    "гл":                   WORD_TYPES.VERB,
    "прил":                 WORD_TYPES.ADJECTIVE,
    "прилагательное":       WORD_TYPES.ADJECTIVE,
    "наречие":              WORD_TYPES.ADVERB,
    "предикатив":           WORD_TYPES.PREDICATIVE,
    "союз":                 WORD_TYPES.CONJUNCTION,
    "предлог":              WORD_TYPES.PREPOSITION,
    "местоимение":          WORD_TYPES.PRONOUN,
    "мест":                 WORD_TYPES.PRONOUN,
    "междометие":           WORD_TYPES.INTERJECTION,
    "частица":              WORD_TYPES.PARTICLE,
    "прич":                 WORD_TYPES.PARTICLE,
    "артикль":              WORD_TYPES.ARTICLE,
    "числительное":         WORD_TYPES.NUMERAL,
    "числ":                 WORD_TYPES.NUMERAL,
}


"""
{{сущ ru m a 1b
|основа=кот
|основа1=кот
|слоги={{по-слогам|кот}}
}}

{{морфо-ru|кот|и=т}}
"""

def t_noun_cb(section, t, label, word):
    # сущ ru m a 1a 
    # https://ru.wiktionary.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D1%81%D1%83%D1%89-ru
    word.Type = WORD_TYPES.NOUN
    log.debug("word.Type: %s", word.Type)

    splits = t.name.split(" ")
    
    for s in splits:
        # lang
        if s in ("ru"):
            word.LanguageCode = s
        
        # мужское / женское
        if s in ("м", "m", "мо"):
            word.IsMaleVariant = True

        elif s in ("ж", "f", "жо"):
            word.IsFemaleVariant = True

        elif s in ("с", "n", "со"):
            word.IsNeuterVariant = True

        # одушевленное / неодушевленное
        if s in ("a", "мо", "жо", "со", "мо-жо", "одуш"):
            word.is_soul = True

        elif s in ("ina", "неод"):
            word.is_soul = False
        
        # тип словоизменения 
        if s is not None:
            if len(s) > 0:
                if s[0] == '0':
                    # 0
                    pass
                    
                if s[0] == '1':
                    # 1 — слова с основой на твёрдый согласный (топор, комод, балда, кобра, олово, пекло; твёрдый, тусклый)
                    pass
                    
                elif s[0] == '2':
                    # 2 — слова с основой на мягкий согласный (тюлень, искатель, цапля, Дуня, горе, поле; весенний)
                    pass

                elif s[0] == '3':
                    # 3 — слова с основой на г, к или х (сапог, коряга, парк, моллюск, золотко, петух, неряха; мягкий)
                    pass

                elif s[0] == '4':
                    # 4 — слова с основой на ж, ш, ч, щ (калач, лаваш, галоша, святоша, жилище, вече, вящий)
                    pass

                elif s[0] == '5':
                    # 5 — слова с основой на ц (немец, конец, девица, деревце, куцый)
                    pass

                elif s[0] == '6':
                    # 6 — слова с основой на гласный (кроме и) или й/j (бой, край; шея, здоровье)
                    pass

                elif s[0] == '7':
                    # 7 — слова с основой на и (полоний, сложение, мания, удостоверение)
                    pass

                elif s[0] == '9':
                    # 8 — слова с традиционным «3-м склонением» (боль, тетрадь, зыбь; имя; путь)
                    pass

            if len(s) > 1:
                if s[0].isnumeric():
                    for c in s[1:]:
                        if c == '*':
                            pass
                        elif c == '°':
                            pass
                        elif c == "'":
                            pass
                        elif c == "(":
                            pass
                        elif c == '-':
                            pass
                        elif c == '+':
                            pass
                        elif c == ',':
                            pass
                        elif c == 'a':
                            # a — ударение всегда на основу (парад, спонсор, мама, солнце, платёжный)
                            pass
                        elif c == 'b':
                            # b — ударение всегда вне основы, если кроме основы вообще что-либо есть (топор, похвала, вещество, родной)
                            pass
                        elif c == 'c':
                            # c — ударение на основу в ед. ч. и вне основы во мн. ч. (дар, место, поле)
                            pass
                        elif c == 'd':
                            # d — ударение на окончание в ед. ч. и на основу во мн. ч. (заря)
                            pass
                        elif c == 'e':
                            # e — ударение на основу в ед. ч. и им. п. мн. ч., вне основы в остальных падежах мн. ч. (корень, новость)
                            pass
                        elif c == 'f':
                            # f — ударение на основу в им. п. мн. ч. и вне основы в остальных случаях.
                            pass
        
        # 1*a, 1*b
        # 1°, 2°
        # 1b÷, 2b÷
        # 1b?, 2b?
        # 6*b^
        # <ДОПОЛНИТЬ!>
    

def t_verb_cb(section, t, label, word):
    # гл ru 1a
    # https://ru.wiktionary.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D1%81%D1%83%D1%89-ru
    word.Type = WORD_TYPES.VERB

    splits = t.name.split(" ")
    
    for s in splits:
        # lang
        if s in ("ru"):
            lang = s
            
        # morph
        if len(s) > 0:
            c = s[0]
            
            if c.isnumeric():
                n = get_number(c)


def t_adj_cb(section, t, label, word):
    # прил ru 1a
    word.Type = WORD_TYPES.ADJECTIVE

    splits = t.name.split(" ")
    
    for s in splits:
        # lang
        if s in ("ru"):
            lang = s
            
            
def t_part_cb(section, t, label, word):
    # прич ru 1a
    word.Type = WORD_TYPES.PARTICLE

    splits = t.name.split(" ")
    
    for s in splits:
        # lang
        if s in ("ru"):
            lang = s
    
    
def t_pronoun_cb(section, t, label, word):
    # мест ru 1a
    word.Type = WORD_TYPES.PRONOUN

    splits = t.name.split(" ")
    
    for s in splits:
        # lang
        if s in ("ru"):
            lang = s
    
    
def t_numeral_cb(section, t, label, word):
    # числ ru 1a
    word.Type = WORD_TYPES.NUMERAL

    splits = t.name.split(" ")
    
    for s in splits:
        # lang
        if s in ("ru"):
            lang = s
    

def t_adv_cb(section, t, label, word):
    word.Type = WORD_TYPES.ADVERB
    


def t_inflection_cb():
    """
    {{inflection сущ ru
    <noinclude>|шаблон-кат=1</noinclude>
    |form={{{form|}}}
    |case={{{case|}}}
    |nom-sg= |nom-pl=
    |gen-sg= |gen-pl=
    |dat-sg= |dat-pl=
    |acc-sg= |acc-pl=
    |ins-sg= |ins-pl=
    |prp-sg= |prp-pl=
    |loc-sg=
    |voc-sg=
    |prt-sg=
    |П=
    |Пр=
    |Сч=
    |hide-text=
    |зачин=
    |слоги=
    |кат=
    |род=
    |скл=
    |зализняк=
    |зализняк1=
    |чередование=
    |pt=
    |st=
    |затрудн=
    |коммент=
    |клитика=
    }}
    """
    pass



word_type_templates = {
    "сущ"       : t_noun_cb,
    "сущ-ru"    : t_noun_cb,
    "прил"      : t_adj_cb,
    "гл"        : t_verb_cb,
    "форма-гл"  : t_verb_cb,
    "прич"      : t_part_cb,
    "мест"      : t_pronoun_cb,
    "числ"      : t_numeral_cb,
    "adv"       : t_adv_cb,
}


def get_translations(section, label):
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
                    lang = t.arg(0)
                    term = t.arg(1)

                    if term:
                        result.append((lang, term))

                elif t.name == "t+":
                    # {{t+|zu|ihhashi|c5|c6}}
                    lang = t.arg(0)
                    term = t.arg(1)

                    if term:
                        result.append((lang, term))

                elif t.name == "t":
                    # {{t|ude|муи }}
                    lang = t.arg(0)
                    term = t.arg(1)

                    if term:
                        result.append((lang, term))

                elif t.name == "перев-блок":
                    # {{перев-блок|lang=term}}
                    for a in t.args:
                        lang = a.get_name()
                        term = a.get_value()

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


def get_conjugations(section, label):
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
            result += templates.en_conj(t, label)

        elif t.name == "en-verb":
            (third, present_participle, simple_past, past_participle) = templates.en_verb(t, label)
            result.append(third)
            result.append(present_participle)
            result.append(simple_past)
            result.append(past_participle)

    # unique
    result = unique(result)

    return result if result else None


def is_male_variant(section, label):
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
            (head, gender, plural, plural2) = templates.ang_noun(t, label)

            if gender == "m":
                return True

    return None

def is_female_variant(section, label):
    # From {{inh|en|enm|cat}}, {{m|enm|catte}},
    # from {{inh|en|ang|catt||male cat}}, {{m|ang|catte||female cat}},
    # from {{inh|en|gem-pro|*kattuz}}.
    for t in section.find_objects(Template, recursive=True):
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label)

            if gender == "f":
                return True

    return None


def is_singular(section, label):
    # case 1
    for t in section.find_objects(Template, recursive=True):
        if t.name == "en-noun" and False: # disabled
            # case 1
            (s, p, is_uncountable) = templates.en_noun(t, label)

            if p:
                return True

        elif t.name == "head":
            # case 2
            lang = t.arg(0)
            flag = t.arg(1)
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

                v = t.arg(k)

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


def is_plural(section, label):
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

                v = t.arg(k)

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


def is_verb_present(section, label):
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

                v = t.arg(k)

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


def is_verb_past(section, label):
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
            a3 = t.arg(2)
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

                v = t.arg(k)

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


def is_verb_futur(section, label):
    return None


def get_singular_variant(section, label):
    return None


def get_plural_variant(section, label):
    for t in section.find_objects(Template, recursive=True):
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label)

            if plural is not None:
                return unique(plural)

        elif t.name == "en-noun":
            (single, plural, is_uncountable) = templates.en_noun(t, label)

            if plural:
                return unique(plural)

    return None


def get_alternatives(section, label):
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
                lang = t.arg(0)
                term = t.arg(1)

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
            lang = t.arg(0)
            term = t.arg(1)

            if term:
                result.append((lang, term))

    #
    result = [ term for (lang, term) in result if lang == "ru" or lang is None ]

    return result if result else None


def get_related(section, label):
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
                                lang = t.arg(0)
                                term = t.arg(1)

                                if term:
                                    result.append((lang, term))
            break

    # case 2
    # {{rel-top|related terms}}
    for sec in section.find_section("родственные слова", recursive=True):
        for t in sec.find_objects(Template, recursive=True):
            # * {{l|en|hower}}
            if t.name == "l":
                lang = t.arg(0)
                term = t.arg(1)

                if term:
                    result.append((lang, term))

            elif t.name == "родств-блок":
                for a in t.args():
                    term = a.get_value()
                    if term:
                        result.append((None, term))

    # case 3
    # {{en-simple past of|do}}
    for t in section.find_objects(Template, recursive=True):
        # * {{l|en|hower}}
        if t.name == "en-simple past of":
            lang = t.arg("lang")
            term = t.arg(0)

            if term:
                result.append((lang, term))

        elif t.name == "present participle of":
            # {{present participle of|do}}
            lang = t.arg("lang")
            term = t.arg(0)

            if term:
                result.append((lang, term))

        elif t.name == "en-third-person singular of":
            # {{en-third-person singular of|do}}
            lang = t.arg("lang")
            term = t.arg(0)

            if term:
                result.append((lang, term))

        elif t.name == "inflection of":
            # {{inflection of|do||past|part|lang=en}}
            lang = t.arg("lang")
            term = t.arg(0)

            if term:
                result.append((lang, term))

    # case 4
    # get from parents
    """
    for t in section.find_templates_in_parents():
        if t.name == "m":
            # {{m|en|doe|t=female deer}}
            lang = t.arg(0)
            term = t.arg(1)

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

    result = unique( bylang.get("ru", []) + bylang.get(None, []) )

    return result if result else None


def get_synonyms(section, label):
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

    ====Синонимы====
    * {{sense|period of sixty minutes|a season or moment}} {{l|en|stound}} {{qualifier|obsolete}}
    """

    result = []

    # here is section like a ====Noun==== or ====Verb====
    # find section =====Synonyms=====
    for sec in section.find_section("синонимы", recursive=True):
        for t in sec.find_objects(Template, recursive=True):
            # find {{sense|animal}} | {{l|en|horsie}}
            # remove brackets like a [[...]]
            # remove templates
            # get example
            if 0 and t.name == "sense":  # disabled, because words only
                lang = t.arg(0)
                term = t.arg(1)

                if term:
                    result.append((lang, term))

            elif t.name == "l":
                lang = t.arg(0)
                term = t.arg(1)

                if term:
                    result.append((lang, term))

    # case 2
    for t in section.find_objects(Template, recursive=True):
        if t.name in ("syn", "syn2", "syn3", "syn4", "syn5", "syn1",
                          "syn2-u", "syn3-u", "syn4-u", "syn5-u"):
            lang = t.arg("lang")
            for a in t.args():
                result.append(  (lang, a.get_value() ) )

    # case 3
    for sec in section.find_section("синонимы", recursive=True):
        for link in sec.find_objects(Link, recursive=True):
                lang = None
                term = link.get_text()

                if term:
                    result.append((lang, term))

    # filter "ru"
    result = [ term for (lang, term) in result if lang == "ru" or lang is None ]
    result = unique(result)

    return result if result else None


def tscan(lang, section, label):
    word = Word()
    word.LabelName = label
    word.LanguageCode = lang
    words = [ word ]
    
    for obj in section.find_objects((Section, Template), recursive=True):
        if isinstance(obj, Section):
            sec = obj
            if sec.name.startswith("{{з|"):
                # word type section. recursive
                words += tscan(lang, sec, label)

            elif sec.name == "значение":
                for li in sec.find_objects(Li):
                    word.add_explaniation( li ) # will be cloned later

            elif sec.name == "синонимы":
                for link in sec.find_objects(Link):
                    word.add_synonym(link.get_text())

            elif sec.name == "родственные слова":
                for link in sec.find_objects(Link):
                    word.add_related(link.get_text())
                
        elif isinstance(obj, Template):
            t = obj
            
            splits = t.name.split(" ")
            log.debug("splits: %s", repr(splits))
            
            word_type_cb = word_type_templates.get(splits[0], None)
            
            if word_type_cb is not None:
                # it is wort type section
                word_type_cb(section, t, label, word)

            elif t.name == "перев-блок":
                for a in t.args():
                    word.add_translation( a.get_name(), a.get_value() )

    # explainations case 2
    for li in section.find_objects(Li):
        word.add_explaniation( li ) # will be cloned later
        
    # cloning. new word for each explaination
    result = []
    
    return words

