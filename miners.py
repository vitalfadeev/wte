#!/usr/bin/python3
# -*- coding: utf-8 -*-

from itertools import islice
from collections.abc import Iterable
from wikoo import Section, Template, Link, Li, Dl, Dt, Dd, String
from helpers import convert_to_alnum, proper, deduplicate
from helpers import remove_comments, extract_from_link
from helpers import first_true


def find_terms(section, sub_section_name, templates, links=False):
    """ 
    for (lang, term) in find_terms( section, "traducciones", { 
            't' : [['lang', 0], [1]],
            't+': t_plus_cb,
        } ):
        print( lang, term )
    """
    def find_args(t, keys):
        for k in keys:
            value = t.arg(k)
            if value is not None:
                yield value        
        
    # find subsection
    for sub_section in section.find_objects(Section, recursive=True):
        if sub_section.name == sub_section_name:
            # find templates
            for t in sub_section.find_objects(Template, recursive=True):
                # find arguments
                ts = templates.get(t.name, None)
                if callable(ts):
                    yield from ts(t)
                    
                elif isinstance(ts, Iterable):
                    (lang_keys, term_keys) = ts
                    # find first valid lang
                    lang = next(find_args(t, lang_keys), None)

                    # find all terms
                    for term in find_args(t, term_keys):
                        yield (lang, term)

            # find links
            for link in sub_section.find_objects(Link, recursive=True):
                term = link.get_text().strip()
                if term:
                    yield (None, term)                


def has_flag_in_name(search_context, excludes, flag):
    """ has_flag_in_name(section, [], "singular") """
    if search_context.name.find(flag) != -1:
        return True


def has_template_with_flag(search_context, excludes, flag):
    """ has_template_with_flag(section, [] "singular") """
    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        if t.name.find(flag) != -1:
            return True
            

def has_arg(t, excludes, keys, *checkers):
    """ has_arg(t, [], "m") """
    # "lang" -> ["lang"]. 0 -> [0]
    if isinstance(keys, (str, int)):
        keys = [keys]
    
    for key in keys:
        value = t.arg(key)
        if value:
            if checkers:
                for checker in checkers:
                    func = checker[0]
                    params = checker[1:]
                    result = func(value, excludes, *params) # OK
                    if result:
                        return True # OK
            else:
                return True # OK
        

def has_flag(s, excludes, flags, *checkers):
    """ has_flag(a, [], "presente") """
    if isinstance(flags, (str, int)):
        flags = [flags]
        
    for flag in flags:
        if s and s.find(flag) != -1:
            return True
        

def has_value(s, excludes, values, *checkers):
    """ has_flag(a, [], "presente") """
    if isinstance(values, (str, int)):
        values = [values]
        
    if s in values:
        return True
        

def has_arg_with_flag_in_name(t, excludes, flag):
    return any( a for a in t.args() if a.name is not None and a.name.find(flag) != -1 )


def has_arg_and_value_contain(t, excludes, arg_name, flag):
    """ has_arg(t, "m") """
    value = t.arg(arg_name)
    if value:
        if isinstance(flag, str):
            if value.lower().find(flag) != -1:
                return True
        elif isinstance(flag, Iterable):
            for f in flag:
                if value.lower().find(f) != -1:
                    return True
        else:
            assert 0, "unsupported"

        
def has_section(search_context, excludes, names, *checkers):
    if isinstance(names, str):
        names = [names]

    # find template
    for sec in search_context.find_objects(Section, recursive=True, exclude=excludes):
        # check name
        if sec.name in names:
            # check args
            if checkers:
                for checker in checkers:
                    func = checker[0]
                    params = checker[1:]
                    result = func(sec, excludes, *params)
                    if result:
                        return True # OK                
            else:
                return True # OK


def has_template(search_context, excludes, tnames, *checkers):
    """ has_template(section, [], "g") """
    if isinstance(tnames, str):
        tnames = [tnames]
    
    # find template
    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        # check name
        if t.name in tnames:
            # check args
            if checkers:
                for checker in checkers:
                    func = checker[0]
                    params = checker[1:]
                    result = func(t, excludes, *params)
                    if result:
                        return True # OK                
            else:
                return True # OK


def has_flag_in_explaination(search_context, excludes, flags, *args):
    """ has_flag_in_explaination(section, [], "maschile") """
    # find one levels Li 
    if isinstance(flags, str):
        flags = [flags]
        
    if isinstance(search_context, (Li, Dl)):
        for flag in flags:
            if search_context.get_text().find(flag) != -1:
                return True


def has_flag_in_text(search_context, excludes, flags):
    """ has_flag_in_text(section, [], "''m inv''") """
    if isinstance(flags, str):
        flags = [flags]
        
    for s in search_context.find_objects(String, recursive=False, exclude=excludes):
        for flag in flags:
            if s.get_text().find(flag) != -1:
                return True


def has_flag_in_text_recursive(search_context, excludes, flags):
    """ has_flag_in_text_recursive(section, [], "''m inv''") """
    if isinstance(flags, str):
        flags = [flags]
        
    for s in search_context.find_objects(String, recursive=True, exclude=excludes):
        for flag in flags:
            if s.get_text().find(flag) != -1:
                return True


def if_any(search_context, excludes, *args):
    """ 
    if_any(section, 
        [has_template, "m"], 
        [has_template, "mf"]
    ) 
    """
    for a in args:
        checker = a[0]
        params = a[1:]
        result = checker(search_context, excludes, *params)
        if result:
            return True
    

#########################################################
def term0_cb(t):
    lang = None
    term = t.arg(0)
    yield (lang, term)

def term1_cb(t):
    lang = None
    term = t.arg(0)
    yield (lang, term)

def lang0_term1_cb(t):
    lang = t.arg(0)
    term = t.arg(1)
    if term is not None:
        yield (lang, term)

def lang0_term2_cb(t):
    lang = t.arg(0)
    term = t.arg(2)
    yield (lang, term)

def w_cb(t):
    lang = t.arg("lang")
    term = t.arg(0)
    yield (lang, term)

def t_plus_cb(t):
    # {{t+|en|1|cat|,|3, 4|hooker|,|5|john|,|7|jack|,|8|noughts and crosses|,|8|tic-tac-toe}}
    # {{t+|de|1, 2|Katze|f|,|1|Kater|m|nota|gato macho|,|7|Wagenheber|m|,|7|Heber|m|,|8|Kreis und Kreuz|,|8|Tic Tac Toe}}
    # {{t+|de|Dezember|m}}, {{t+|de|Julmond|m}}
    # first
    lang = t.arg(0)
    term = t.arg(2)
    if term is not None:
        yield (lang, term)
    
    # delimited
    gen = t.args()
    for a in gen:
        value = a.get_value()
        if value.strip() == ',': # block start
            try:
                n = next(gen).get_value()
                term = next(gen).get_value()
                if term is not None:
                    yield (lang, term)
            except StopIteration:
                break

def alter_cb(t):
    lang = t.arg(0)
    args = t.args()
    next(args, None)
    for a in args:
        term = a.get_value().strip()
        if len(term) == 0:
            break
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



##########################################################
def find_explainations(tos_section, is_expl_section):
    is_found = False
    
    # case 1: try li from ==={{Bedeutungen}}=== first
    for expl_section in tos_section.find_objects(Section, recursive=True):
        if is_expl_section(expl_section):
            for li in expl_section.find_objects(Li, recursive=False):
                is_found = True
                yield li
            break
            
    if not is_found:
        # case 2: try get list in TOS section
        for li in tos_section.find_objects(Li, recursive=False):
            is_found = True
            yield li

    # case 3: try get Dl in TOS section
    if not is_found:
        for dl in tos_section.find_objects(Dl, recursive=False):
            is_found = True
            yield dl


def get_label_type(expl):
    list1 = []
    for t in expl.find_objects((Template, Link), recursive=True, exclude=[li for li in expl.find_objects((Li, Dl))]):
        inner = t.get_text()
        s = convert_to_alnum(inner)
        s = deduplicate(s)
        s = s.strip("_").strip()
        splitted = s.split(" ")
        list1 += [ w.upper() for w in splitted ]

    list2 = []
    for l in expl.find_objects(Link, recursive=True, exclude=[li for li in expl.find_objects((Li, Dl))]):
        inner = l.get_text()
        s = convert_to_alnum(inner)
        s = deduplicate(s)
        s = s.strip("_").strip()
        splitted = s.split("_")
        list2 += [ proper(w) for w in splitted ]

    list3 = []
    s = expl.get_raw()
    s = s.replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    s = convert_to_alnum(s)
    s = deduplicate(s)
    s = s.strip("_").strip()
    splitted = s.split("_")
    list3 += [ w.lower() for w in splitted ]
    list3 = [ w for w in list3 if len(w) >= 3 ]

    # Concat
    biglst = list1 + list2 + list3

    if len(biglst) == 1:
        return biglst[0]

    elif len(biglst) >= 2:
        return "-".join(biglst[:2])

    else:
        return ""


#
def find_all(section, excludes, *miners):
    """ [in_template, "sinónimos", [in_arg, [0,1,2,3,4,5,6,7,8,9,10,11,12]]] """
    for miner in miners:
        func = miner[0]
        params = miner[1:]
        yield from func(section, excludes, *params)


def find_any(section, excludes, *miners):
    """ [in_template, "sinónimos", [in_arg, [0,1,2,3,4,5,6,7,8,9,10,11,12]]] """
    for miner in miners:
        func = miner[0]
        params = miner[1:]
        for result in filter(None, func(section, excludes, *params)):
            yield result
            break


def in_section(root, excludes, names, *miners):
    """ in_section(section, [], "véase también") """
    if isinstance(names, str):
        names = [names]
        
    for sec in root.find_objects(Section, recursive=True, exclude=excludes):
        if sec.name in names:
            for miner in miners:
                func = miner[0]
                params = miner[1:]
                yield from func(sec, excludes, *params)


def in_template(root, excludes, names, *miners):
    """ in_template(section, [], "sinónimos") """
    if isinstance(names, str):
        names = [names]
        
    for t in root.find_objects(Template, recursive=True, exclude=excludes):
        if t.name in names:
            for miner in miners:
                func = miner[0]
                params = miner[1:]
                yield from func(t, excludes, *params)


def in_arg(t, excludes, keys, *miners):
    """ in_arg(t, [], ["lang", 0], 1) """
    # miner = [search_context, excludes, filter, miner]
    (lang_keys, term_keys) = keys
    
    # lang
    lang_keys = lang_keys if isinstance(lang_keys, (list, tuple)) else [lang_keys]
    for key in lang_keys:
        if key is not None:
            lang = t.arg(key)
            if lang:
                break
    else:
        lang = None
            
    # term
    term_keys = term_keys if isinstance(term_keys, (list, tuple)) else [term_keys]
    for key in term_keys:
        term = t.arg(key)
        if term:
            term = term.strip()
            yield (lang, term)


def in_arg__old(t, excludes, name, miners=None):
    """ in_arg(t, [], 0) """
    # search_context, excludes, filter, [miner]
    # miner = [search_context, excludes, filter, miner]
    if isinstance(name, int): # positional
        for (i, a) in enumerate(t.positional_args()):
            if i == name:
                if miners:
                    miner = miners[0]
                    params = miners[1:]
                    yield from miner(a, excludes, *params)
                else:
                    term = a.get_value()
                    yield (None, term)
                break
                
    elif isinstance(name, str): # named
        for a in t.args():
            if a.name == name:
                if miners:
                    miner = miners[0]
                    params = miners[1:]
                    yield from miner(l, excludes, *params)
                else:
                    term = a.get_value()
                    yield (None, term)
                break
                
    elif isinstance(name, Iterable): # [] | ()
        for na in name:
            yield from in_arg(t, excludes, na, miners)
        
    else:
        assert 0, "unsupported"


def in_arg_with_flag_in_value(t, excludes, flag, miners=None):
    """ in_arg_with_flag_in_value(t, [], "forma plural de") """
    for a in t.args():
        value = a.get_value().lower()
        if value is not None and value.find(flag) != -1:
            if miners:
                miner = miners[0]
                params = miners[1:]
                yield from miner(a, excludes, *params)
            else:
                term = a.get_value()
                yield (None, term)
            break


def in_link(root, excludes, name=None, *miners):
    """ in_link(section, []) """
    for l in root.find_objects(Link, recursive=True, exclude=excludes):
        if miners:
            for miner in miners:
                func = miner[0]
                params = miner[1:]
                yield from func(l, excludes, *params)
        else:
            term = l.get_text()
            yield (None, term)
            

def in_t_plus(t, excludes, name=None, miners=None):
    yield from t_plus_cb(t)


def in_callback(t, excludes, name=None, miners=None):
    yield from name(t)


MINERS = {
    "cog"       : lang0_term1_cb,
    "l"         : lang0_term1_cb,  # {{l|cs|háček}} | {{l|en|go|went}} - word go section #went
    "lb"        : lang0_term1_cb,  # {{label|en|foobarbazbip}}
    "lbl"       : lang0_term1_cb,
    "l-self"    : lang0_term1_cb,
    "m-self"    : lang0_term1_cb,
    "label"     : lang0_term1_cb,
    "m"         : lang0_term1_cb,  # {{m|en|word}}
    "rootsee"   : lang0_term1_cb,
    "jump"      : lang0_term1_cb,  # {{jump|fr|combover|s|a}}
    "link"      : lang0_term1_cb,
    "soplink"   : term0_cb,  # {{soplink|foo|/|bar|baz|-} → foo/bar baz-
    "pedlink"   : lang0_term1_cb,
    "pedia"     : term0_cb,
    "w"         : w_cb,
    # *{{w|William Shakespeare|Shakespeare}} | *{{w|William Shakespeare|Shakespeare|lang=fr}} | *{{w|lang=fr|William Shakespeare|Shakespeare}}
    "wikipedia" : term0_cb,  # {{wikipedia|article|link title}}
    "wikispecies":term0_cb,

    "ü"         : lang0_term1_cb,
    "üt"        : lang0_term1_cb,        
    "t"         : lang0_term1_cb,
    "t*"        : lang0_term1_cb,
    "t+"        : t_plus_cb,
    "t+check"   : t_plus_cb,
    "t+tt"      : t_plus_cb,
    "t-check"   : lang0_term1_cb,
    "t-check-egy":lang0_term1_cb,
    "t-egy"     : lang0_term1_cb,
    "t-f"       : lang0_term1_cb,
    "t-image"   : lang0_term1_cb,
    "t-needed"  : lang0_term1_cb,
    "t-sile"    : lang0_term1_cb,
    "t-simple"  : lang0_term1_cb,
    "t-tpi"     : lang0_term1_cb,
    "trad+"     : lang0_term1_cb,
    "trad-"     : lang0_term1_cb,
    "trad--"    : lang0_term1_cb,
    "trad"      : lang0_term1_cb,

    "s"         : lang0_term1_cb,
    "syn"       : lang0_term1_cb,
    "synonym of": lang0_term1_cb,

    "alter"     : alter_cb,
    "alternative form of": lang0_term1_cb,
    "en-conj"   : en_conj_cb,
    "form of"   : lang0_term2_cb,  # {{form of|en|alternative form|word}}
    "given name": term1_cb,  # {{given name|en|male}}.
    "head"      : lang0_term1_cb,
    "rhymes"    : lang0_term1_cb,
}

