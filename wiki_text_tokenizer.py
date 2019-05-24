#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Layout:    https://en.wiktionary.org/wiki/Wiktionary:Entry_layout
# Templates: https://en.wiktionary.org/wiki/Wiktionary:Templates
# Semantic:  https://en.wiktionary.org/wiki/Wiktionary:Semantic_relations
# Examples:  https://en.wiktionary.org/wiki/Wiktionary:Example_sentences
#            https://en.wiktionary.org/wiki/Template:examples-right

# Algorithm:
# - read text
# - tokenize templates: {{ }}
# - tokenize preformatted: <space>...
# - tokenize tables: {| |}
# - tokenize format elements: links [[ ]], '' '', _( )_
# - tokenize headrs: == ==
# - tokenize lists: #, *
# - tokenize sections: <Header>, <Header>


# = =       ->  = =
# {{ }}     -> {{ }}
# = {{ =    -> = =
# = {{ }} = -> {{ }} = =
# = {{ = }} -> = =
# = = {{ }} -> = = {{ }}
# {{ = }} = -> {{ }}
# =         ->
# = {{      ->
# = {{ }}   -> {{ }}

# # List\n   -> # List\n
# # {{ }}\n  -> {{ }}    # List {{ }}\n
# # {{\n}}\n -> {{\n}}   # {{\n}}\n
# # {{\nEOF  -> # {{\n
# # {{\n# 2  -> # {{\n   # 2
# # {{\n## 2 -> ## 2     # {{\n## 2


# a[0..65536] -> []
#
# a = [None]*65536

# opened = [] # pos: marker
# expect = [] # pos: (opened_pos, marker)

# test open
# test expect

import logging
import os

from wte import Word
from wte import WORD_TYPES
import templates


TXT_FOLDER = "txt"  # folder where stored text files for debugging
CACHE_FOLDER = "cached"  # folder where stored downloadad dumps
LOGS_FOLDER = "logs"  # log folder

# logging
log_level = logging.INFO  # log level: logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR
WORD_JUST = 24  # align size


def setup_logger(logger_name, level=logging.INFO, msgformat='%(message)s'):
    l = logging.getLogger(logger_name)

    logging.addLevelName(logging.DEBUG, "DBG")
    logging.addLevelName(logging.INFO, "NFO")
    logging.addLevelName(logging.WARNING, "WRN")
    logging.addLevelName(logging.ERROR, "ERR")

    logfile = logging.FileHandler(os.path.join(LOGS_FOLDER, logger_name + ".log"), mode='w', encoding="UTF-8")
    formatter = logging.Formatter(msgformat)
    logfile.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(logfile)

    return l

def create_storage(folder_name):
    """
    Create folders recusively.

    In:
      folder_name: Storage folder name

    """
    if (not os.path.exists(folder_name)):
        os.makedirs(folder_name, exist_ok=True)

# setup loggers
create_storage(LOGS_FOLDER)
create_storage(TXT_FOLDER)
logging.basicConfig(level=log_level)
log             = setup_logger('main', msgformat='%(levelname)s: %(message)s')
log_non_english = setup_logger('log_non_english')
log_unsupported = setup_logger('log_unsupported')
log_no_words    = setup_logger('log_no_words')





EOF = "^Z"

HEADER7         = 1
HEADER6         = 2
HEADER5         = 3
HEADER4         = 4
HEADER3         = 5
HEADER2         = 6
HEADER1         = 7
LINK            = 8
TEMPLATE        = 9
ITALIC2         = 10
ITALIC          = 11
BOLD_ITALIC     = 12
BOLD            = 13
OLI             = 14
ULI             = 15
PREFORMATED     = 16
TABLE           = 17
TABLE_CAPTION   = 18
TABLE_HEADER    = 19
TABLE_SPLITTER  = 20
TABLE_CELL      = 21
TAG_CLOSED      = 22
TAG             = 23
DEFS            = 24
ISBN            = 25
RFC             = 26

OPENED = 1
CLOSED = 2
RESET  = 3

marks = [
    # start,        end,        reset,      id,             inside
    ("\n=======",   "=======",  "\n",       HEADER7,        None),  # header 7
    ("\n======",    "======",   "\n",       HEADER6,        None),  # header 6
    ("\n=====",     "=====",    "\n",       HEADER5,        None),  # header 5
    ("\n====",      "====",     "\n",       HEADER4,        None),  # header 4
    ("\n===",       "===",      "\n",       HEADER3,        None),  # header 3
    ("\n==",        "==",       "\n",       HEADER2,        None),  # header 2
    ("\n=",         "=",        "\n",       HEADER1,        None),  # header 1
    ("[",           "]",        EOF,        LINK,           None),  # link
    ("{{",          "}}",       EOF,        TEMPLATE,       None),  # template
    ("_(",          ")_",       EOF,        ITALIC2,        None),  # italic
    ("'''''",       "'''''",    EOF,        BOLD_ITALIC,    None),  # bold italic
    ("'''",         "'''",      EOF,        BOLD,           None),  # bold
    ("''",          "''",       EOF,        ITALIC,         None),  # italic
    ("\n#",         "\n",       None,       OLI,            None),  # ordered li
    ("\n*",         "\n",       None,       ULI,            None),  # unordered li
    ("\n ",         "\n",       None,       PREFORMATED,    None),  # preformated
    ("\n{|",        "|}",       None,       TABLE,          None),  # table
    ("\n|+",        "\n",       None,       TABLE_CAPTION,  TABLE), # table caption
    ("\n!",         "\n",       None,       TABLE_HEADER,   TABLE), # table header
    ("\n|-",        "\n",       None,       TABLE_SPLITTER, TABLE), # table row splitter
    ("\n|",         "\n",       None,       TABLE_CELL,     TABLE), # table cell
    ("</",          ">",        EOF,        TAG_CLOSED,     None),  # closed tag
    ("<",           ">",        EOF,        TAG,            None),  # tag
    ("\n;",         "\n",       None,       DEFS,           None),  # defs
    ("\n:",         "\n",       None,       DEFS,           None),  # defs
#    ("ISBN ",       "![0-9]",   "![0-9]",   ISBN,           None),  # ISBN id
#    ("RFC ",        "![0-9]",   "![0-9]",   RFC,            None),  # RFC id
]

class Container:
    def __init__(self, spos, epos):
        self.name = ""
        self.childs = []
        self.parent = None
        self.spos = spos
        self.epos = epos

    def add_child(self, child):
        # add. keep ordered
        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self

        # keep ordered
        for i, ch in enumerate(self.childs):
            if ch.spos > child.spos:
                self.childs.insert(i, child)
                break
        else:
            self.childs.append(child)

    def remove_child(self, child):
        try: self.childs.remove(child)
        except ValueError: pass

    def is_bigger_than(self, other):
        if self.spos <= other.spos and other.epos <= self.epos:
            """
            # not eq. eq is not big
            if self.spos == other.spos and other.epos == self.epos:
                return False
            else:
                return True
            """
            return True
        else:
            return False

    def eat(self, meat):
        if self.is_bigger_than(meat):
            # OK. eat. pass to childs
            for child in self.childs:
                if child.eat(meat):
                    return True # OK. eated

            # Not eated by childs, but eated by self
            # Check for childs can be eated by meat
            i = 0

            while i < len(self.childs):
                child = self.childs[i]
                if meat.is_bigger_than(child):
                    meat.eat(child) # eat child
                else:
                    i += 1

            self.add_child(meat)
            return True # OK. eated

        else:
            return False # FAIL. out

    def find_objects(self, cls, recursive=False):
        for c in self.childs:
            if isinstance(c, cls):
                yield c

            if recursive:
                for obj in c.find_objects(cls, recursive):
                    yield obj

    def find_section(self, name, recursive=False):
        for section in self.find_objects(Section, recursive):
            if section.name == name:
                yield section

    def find_until(self, cls, recursive=False):
        for c in self.childs:
            if isinstance(c, cls):
                break
            else:
                yield c

            # in depth
            if recursive:
                c.find_until(cls, recursive)

    def find_objects_between_templates(self, objtype, name1, name2):
        # {{"trans-top"}}, {{"trans-bottom"}}
        generator = self.find_objects((Template, objtype), recursive=True)

        for t1 in generator:
            if isinstance(t1, Template) and t1.name == name1:
                # OK. found 1
                for obj in generator:
                    if isinstance(obj, Template) and obj.name == name2:
                        # END.
                        return
                    else:
                        if isinstance(obj, objtype):
                            # OK
                            yield obj

    def get_explainations(self):
        for child in self.childs:
            if isinstance(child, Li):
                yield child

class Article(Container):
    def __repr__(self):
        return "Article(" + str(self.spos) + ", " + str(self.epos) + ")"

class Template(Container):
    def arg(self, pos, text):
        if isinstance(pos, int):
            # positional arg
            if pos < len(self.childs):
                # OK
                return self.childs[pos].get_value(text)
            else:
                # FAIL
                return None

        elif isinstance(pos, str):
            # named arg
            for a in self.childs:
                if a.get_name(text) == pos:
                    # OK
                    return a.get_value(text)
            else:
                # FAIL
                return None

        else:
            assert 0, "unsupported"


    def __repr__(self):
        return "Template(" + str(self.spos) + ", " + str(self.epos) + ")"

class String(Container):
    def __repr__(self):
        return "String(" + str(self.spos) + ", " + str(self.epos) + ")"

class Preformatted(Container):
    def __repr__(self):
        return "Preformatted(" + str(self.spos) + ", " + str(self.epos) + ")"

class Link(Container):
    def __repr__(self):
        return "Link(" + str(self.spos) + ", " + str(self.epos) + ")"

class Table(Container):
    def __repr__(self):
        return "Table(" + str(self.spos) + ", " + str(self.epos) + ")"

class Italic(Container):
    def __repr__(self):
        return "Italic(" + str(self.spos) + ", " + str(self.epos) + ")"

class Header(Container):
    def __repr__(self):
        return "Header(" + str(self.spos) + ", " + str(self.epos) + ")"

class Li(Container):
    def get_raw(self, text):
        for obj in self.find_objects(Li):
            # before sublist
            return text[self.spos+1:obj.spos]
        else:
            # text
            return text[self.spos+1:self.epos]

    def __repr__(self):
        return "Li(" + str(self.spos) + ", " + str(self.epos) + ")"

class LiOrdered(Li):
    def __repr__(self):
        return "LiOrdered(" + str(self.spos) + ", " + str(self.epos) + ")"

class LiUnordered(Li):
    def __repr__(self):
        return "LiUnordered(" + str(self.spos) + ", " + str(self.epos) + ")"

class Section(Container):
    def __init__(self, *args, **kvars):
        super().__init__(*args, **kvars)
        self.level = 0
        self.header = None
        self.name = ""

    def __repr__(self):
        return "Section(" + str(self.spos) + ", " + str(self.epos) + ", level:" + str(self.level) + ")"

class Arg(Container):
    def get_name(self, text):
        eqpos = text.find("=", self.spos, self.epos)

        if eqpos != -1:
            return text[self.spos:eqpos]
        else:
            return None

    def get_value(self, text):
        eqpos = text.find("=", self.spos, self.epos)

        if eqpos != -1:
            return text[eqpos+1:self.epos]
        else:
            return text[self.spos:self.epos]

    def __repr__(self):
        return "Arg(" + str(self.spos) + ", " + str(self.epos) + ")"


def get_strings(root):
    """
    in:  Article(0, 100)
    out: [ (ss, se), (ss, se), (ss, se) ]
    """
    ss = root.spos

    cloned = [ c for c in root.childs ]

    for child in cloned:
        log.debug("child: %s", repr(child))
        se = child.spos

        if ss < se:
            log.debug("string 1: %s", repr((ss, se)))
            yield (ss, se)

        ss = child.epos

    # tail string
    if ss < root.epos:
        se = root.epos
        log.debug("string 2: %s", repr((ss, se)))
        yield (ss, se)

def parse_template_args(t, text):
    args = []

    # find splitters
    splitters = []

    for (ss, se) in get_strings(t):
        pos = text.find("|", ss, se)

        while pos != -1:
            splitters.append(pos)
            pos = text.find("|", pos+1, se)

    # args
    spos = t.spos + 2

    for splitter in splitters:
        epos = splitter
        yield Arg(spos, epos)
        spos = epos + 1

    # last
    epos = t.epos - 2
    yield Arg(spos, epos)

def tokenize_templates(text, startpos=0):
    global marks
    i = startpos
    l = len(text) - 1

    #
    opened = [] # (pos, midx)

    #
    while i < l:
        i2 = i+1

        if text[i] == "{" and text[i2] == "{":
            opened.append( i )
            i += 2

        elif text[i] == "}" and text[i2] == "}":
            if opened:
                spos = opened.pop()

                # parse args
                t = Template(spos, i + 2)  # (spos, epos)
                for a in parse_template_args(t, text):
                    t.add_child(a)
                if t.childs:
                    t.name = text[t.childs[0].spos:t.childs[0].epos]
                yield t

                i += 2
            else:
                pass # broken template: }} without {{

        else:
            i += 1


text = """
==The title==
"""
for t in tokenize_templates(text):
    assert 0

text = """
==The title==
"""
for t in tokenize_templates(text):
    assert 0

text = """
{{abc}}
"""
for (i, t) in enumerate(tokenize_templates(text)):
    if i == 0:
        assert isinstance(t, Template)
        assert text[t.spos:t.epos] == "{{abc}}"
    else:
        assert 0

text = """
{{abc{{def}}}}
"""
for (i, t) in enumerate(tokenize_templates(text)):
    if i == 0:
        assert isinstance(t, Template)
        assert text[t.spos:t.epos] == "{{def}}"
    elif i == 1:
        assert isinstance(t, Template)
        assert text[t.spos:t.epos] == "{{abc{{def}}}}"
    else:
        assert 0

text = """
{{abc
|d}}
"""
for (i, t) in enumerate(tokenize_templates(text)):
    if i == 0:
        assert isinstance(t, Template)
        assert text[t.spos:t.epos] == "{{abc\n|d}}"
    else:
        assert 0

text = """
{{abc|d}}
"""
for (i, t) in enumerate(tokenize_templates(text)):
    assert len(t.childs) > 0
    assert isinstance(t.childs[0], Arg)
    for (ai, a) in enumerate(t.childs):
        if ai == 0:
            assert text[a.spos:a.epos] == "abc"
        else:
            assert text[a.spos:a.epos] == "d"

text = """
{{abc|d}}
"""
for t in tokenize_templates(text):
    assert t.arg(0, text) == "abc"
    assert t.arg(1, text) == "d"


def eat( generator ):
    try: prev = next(generator)
    except StopIteration: return

    while 1:
        try: t = next(generator)
        except StopIteration: break

        # t contain prev
        if t.spos <= prev.spos and prev.epos <= t.epos:
            # OK. eat prev
            t.add_child(prev)
        else:
            # new after prev
            yield prev

        prev = t

    if prev:
        yield prev

def dump(text, root, level=0):
    print( "  "*level, root, ":", text[root.spos:root.epos].replace("\n", "\\n"), (root.spos, root.epos))

    for child in root.childs:
        dump(text, child, level+1)


from itertools import chain

text = """{{a}}"""
for (i, t) in enumerate( eat( chain(tokenize_templates(text), [String(0, len(text))] )) ):
    assert t.childs
    assert text[t.childs[0].spos:t.childs[0].epos] == "{{a}}"

text = """
1{{a|{{sub}}}}2
"""
for (i, t) in enumerate( eat( chain(tokenize_templates(text), [String(0, len(text))] )) ):
    assert t.childs
    assert text[t.childs[0].spos:t.childs[0].epos] == "{{a|{{sub}}}}"
    assert t.childs[0].childs
    assert text[t.childs[0].childs[2].spos:t.childs[0].childs[2].epos] == "{{sub}}"

text = """
1 {{a|{{sub}}}} {{def}} {{ghi}} 2
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)
assert article.childs
assert len(article.childs) == 3
assert text[article.childs[0].spos:article.childs[0].epos] == "{{a|{{sub}}}}"
assert text[article.childs[1].spos:article.childs[1].epos] == "{{def}}"
assert text[article.childs[2].spos:article.childs[2].epos] == "{{ghi}}"


def tokenize_block( root, text, openstr, closestr, cls, without_last_chars=0 ):
    log.debug("searching pattern: %s", openstr.replace("\n", "\\n"))
    generator = get_strings(root)

    for (ss, se) in generator:
        log.debug( "gen 1: " + repr((ss, se)) + "'"+text[ss:se].replace("\n", "\\n")+"'" )
        # fin all entries
        i = ss
        l = se

        while i < l:
            # find start
            pos = text.find(openstr, i, se)
            log.debug("pattern start: %d", pos)
            if pos != -1:
                # OK.
                spos = pos

                # find end. in this block
                pos = text.find(closestr, spos + len(openstr), se)
                log.debug("pattern end 1: %d", pos)
                if pos != -1:
                    epos = pos + len(closestr)

                    if without_last_chars:
                        epos -= without_last_chars

                    log.debug("found 1: %s, %s, %s", openstr, repr((spos, epos)), text[spos:epos].replace("\n", "\\n"))
                    yield cls(spos, epos)

                    i = epos
                    continue

                # find end. in next blocks
                for (ss, se) in generator:
                    log.debug( "gen 2: " + repr( (ss, se) ) +  "'"+text[ss:se].replace("\n", "\\n")+"'" )
                    pos = text.find(closestr, ss, se)
                    log.debug( "pattern end 2: %d", pos )
                    if pos != -1:
                        epos = pos + len(closestr)

                        if without_last_chars:
                            epos -= without_last_chars

                        log.debug("found 2: %s, %s, %s", openstr, repr((spos, epos)), text[spos:epos].replace("\n", "\\n"))
                        yield cls(spos, epos)

                        i = epos
                        l = se
                        break
                else:
                    i += 1

                continue

            break


def tokenize_preformatted(root, text):
    for t in tokenize_block(root, text, "\n ", "\n", Preformatted, without_last_chars=len("\n")):
        yield t


text = """
 1
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for pre in tokenize_preformatted(article, text):
    assert text[pre.spos:pre.epos] == "\n 1"


text = """
 1 {{abc}}
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for pre in tokenize_preformatted(article, text):
    assert text[pre.spos:pre.epos] == "\n 1 {{abc}}"


text = """
 1 {{abc
|arg}}
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for pre in tokenize_preformatted(article, text):
    assert text[pre.spos:pre.epos] == "\n 1 {{abc\n|arg}}"


text = """
 1
 2
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for (i, pre) in enumerate(tokenize_preformatted(article, text)):
    if i == 0:
        assert text[pre.spos:pre.epos] == "\n 1"
    elif i == 1:
        assert text[pre.spos:pre.epos] == "\n 2"


text = """
 1
 2
 3
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for (i, pre) in enumerate(tokenize_preformatted(article, text)):
    res = article.eat(pre)


text = """
 1 {{abc
|arg}}
 2
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for (i, pre) in enumerate(tokenize_preformatted(article, text)):
    if i == 0:
        assert text[pre.spos:pre.epos] == "\n 1 {{abc\n|arg}}"
    elif i == 1:
        assert text[pre.spos:pre.epos] == "\n 2"


text = """
 1
 2
"""
article = Article(0, len(text))
for c in eat( chain(tokenize_templates(text) )):
    article.add_child(c)

for (i, pre) in enumerate(tokenize_preformatted(article, text)):
    if i == 0:
        assert text[pre.spos:pre.epos] == "\n 1"
    elif i == 1:
        assert text[pre.spos:pre.epos] == "\n 2"




def tokenize_tables(root, text):
    for t in tokenize_block(root, text, "\n{|", "\n|}", Table):
        yield t


text = """
 1 
{|
abc
|}
 2
"""
article = Article(0, len(text))

for tpl in tokenize_templates(text):
    article.eat(tpl)

for pre in tokenize_preformatted(article, text):
    article.eat(pre)

for tbl in tokenize_tables( article, text ):
    article.eat(tbl)


def tokenize_format_elements( root, text ):
    # links [ ], '' '', _( )_
    log.debug("tokenize_block [[a]]...")
    for t in tokenize_block(root, text, "[[", "]]", Link):
        yield t

    log.debug("tokenize_block [a]...")
    for t in tokenize_block(root, text, "[", "]", Link):
        yield t

    log.debug("tokenize_block ''a''...")
    for t in tokenize_block(root, text, "''", "''", Italic):
        yield t

    log.debug("tokenize_block _(a)_...")
    for t in tokenize_block(root, text, "_(", ")_", Italic):
        yield t

def tokenize_headrs( root, text ):
    # === Text ===
    generator = get_strings(root)

    for (ss, se) in generator:
        # print( (ss, se), "'"+text[ss:se].replace("\n", "\\n")+"'" )
        # fin all entries
        i = ss
        l = se

        while i < l:
            # find start
            pos = text.find("\n=", i, se)
            # print("pattern start:", pos)
            if pos != -1:
                # OK. header
                spos = pos

                # count level
                i = pos + 2
                level = 1

                while i < l and text[i] == "=":
                    i += 1
                    level += 1

                closestr = "=" * level

                # find end. in this block
                pos = text.find(closestr, i, se)
                # print("pattern end 1:", pos)
                if pos != -1:
                    epos = pos + len(closestr)
                    yield Header(spos, epos)

                    i = epos
                    continue

                # find end. in next blocks
                for (ss, se) in generator:
                    # print( (ss, se), "'"+text[ss:se].replace("\n", "\\n")+"'" )
                    pos = text.find(closestr, ss, se)
                    # print("pattern end 2:", pos)
                    if pos != -1:
                        epos = pos + len(closestr)
                        yield Header(spos, epos)

                        i = epos
                        l = se
                        break
                continue

            break


def get_li_base(s):
    i = 0
    l = len(s)

    level = 0

    while i < l and s[i] in "#*:":
        level += 1
        i += 1

    return s[:level]


def is_li_include(li, other, text):
    # Check for li include other
    b1 = get_li_base(text[li.spos+1:li.epos])
    b2 = get_li_base(text[other.spos+1:other.epos])

    if b2.startswith(b1) and len(b1) < len(b2):
        return True
    else:
        return False

text = """
# 1
## 2
"""
li1 = LiOrdered(1, 4)
li2 = LiOrdered(5, 9)
assert text[li1.spos:li1.epos] == "# 1"
assert text[li2.spos:li2.epos] == "## 2"
assert is_li_include(li1, li2, text)
assert not is_li_include(li2, li1, text)


def tokenize_lists( root, text ):
    # lists
    # # ...
    for t in tokenize_block(root, text, "\n#", "\n", LiOrdered, without_last_chars=len("\n")):
        yield t

    # * ...
    for t in tokenize_block(root, text, "\n*", "\n", LiUnordered, without_last_chars=len("\n")):
        yield t

def find_parent_li(from_li, li, text):
    parent = from_li.parent

    while parent and isinstance(parent, Li):
        if is_li_include(parent, li, text):
            return parent
        else:
            parent = parent.parent

    return None

def eat_lists( root, text ):
    prev = None

    i = 0

    while i < len(root.childs):
        child = root.childs[i]

        if isinstance(child, Li):
            li = child

            if isinstance(prev, Li):
                # check base
                if is_li_include(prev, li, text):
                    prev.epos = li.epos
                    prev.eat(li)
                    prev = li
                    continue
                else:
                    # check parents
                    parent = find_parent_li(prev, li, text)

                    if parent is not None:
                        parent.epos = li.epos
                        parent.eat(li)
                        prev = li
                        continue

        i += 1
        prev = child


def get_header_level(s):
    i = 0
    l = len(s)

    level = 0

    while i < l and s[i] == '=':
        level += 1
        i += 1

    return level


def is_header_level_less_or_eq(a, b, text):
    la = get_header_level(text[a.spos+1:a.epos])
    lb = get_header_level(text[b.spos+1:b.epos])

    if la <= lb:
        return True
    else:
        return False


def eat_sections( root, text ):
    # build tree by levels

    # subsections
    top_section = Section(0, len(text))
    top_section.level = 0
    parent = top_section

    for header in ( e for e in root.childs if isinstance(e, Header) ):
        # find next same level or higher
        section = Section(header.spos, None)
        section.level = get_header_level(text[header.spos+len("\n"):header.epos])
        section.header = header
        section.name = text[header.spos+1:header.epos].strip('=').strip().lower()

        if parent.level < section.level:
            # child section
            parent.add_child( section )
            parent = section

        elif parent.level == section.level:
            # same level section
            parent.parent.add_child( section )
            parent = section

        else:
            # top section
            # find parent
            while parent.level >= section.level:
                parent = parent.parent

            parent.add_child( section )
            parent = section

    # set end pos
    def set_end_pos_recursive(top_section):
        gen = (section for section in top_section.childs )

        for prev in gen:
            for cur in gen:
                prev.epos = cur.spos
                prev = cur

            # last
            top_section.childs[-1].epos = top_section.epos

        # recursive
        for section in top_section.childs:
            set_end_pos_recursive(section)

    set_end_pos_recursive(top_section)

    # eat elements
    def find_section_for_e(top_section, e):
        # check childs
        for c in top_section.childs:
            if c.is_bigger_than(e):
                return find_section_for_e(c, e)

        return top_section

    cloned = [c for c in root.childs]
    for e in cloned:
        section = find_section_for_e(top_section, e)
        section.add_child(e)


    root.add_child(top_section)


def parse(text):
    article = Article(0, len(text))

    log.debug("tokenize_templates...")
    for tpl in tokenize_templates(text):
        article.eat(tpl)

    log.debug("tokenize_preformatted...")
    for pre in tokenize_preformatted(article, text):
        article.eat(pre)

    log.debug("tokenize_tables...")
    for tbl in tokenize_tables(article, text):
        article.eat(tbl)

    log.debug("tokenize_format_elements...")
    for fmt in tokenize_format_elements(article, text):
        article.eat(fmt)

    log.debug("tokenize_headrs...")
    for fmt in tokenize_headrs(article, text):
        article.eat(fmt)

    log.debug("tokenize_lists...")
    for fmt in tokenize_lists(article, text):
        article.eat(fmt)

    log.debug("eat_lists...")
    eat_lists(article, text)

    log.debug("eat_sections...")
    eat_sections(article, text)

    return article

def get_contents(filename):
    """
    Read the file 'filename' and return content.
    """
    with open(filename, encoding="UTF-8") as f:
        return f.read()


def convert_to_alnum(s):
    return "".join( (c if c.isalnum() else "_" for c in s ) )

def deduplicate(s, char='_'):
    """
    in:  "abc__def"
    out: "abc_def"

    in:  "abc_def"
    out: "abc_def"

    in:  "abc_____def"
    out: "abc_def"
    """
    dup = char + char

    while dup in s:
        s = s.replace(dup, char)

    return s

def proper(s):
    if len(s) == 0:
        return s
    elif len(s) == 1:
        return s[0].upper()
    else:
        return s[0].upper() + s[1:].lower()


def get_label_type(expl, text):
    list1 = []
    for t in expl.find_objects(Template):
        inner = text[t.spos+2:t.epos-2]
        s = convert_to_alnum(inner)
        s = deduplicate(s)
        s = s.strip("_").strip()
        splitted = s.split(" ")
        list1 += [ w.upper() for w in splitted ]

    list2 = []
    for t in expl.find_objects(Link):
        inner = text[t.spos+2:t.epos-2]
        s = convert_to_alnum(inner)
        s = deduplicate(s)
        s = s.strip("_").strip()
        splitted = s.split("_")
        list2 += [ proper(w) for w in splitted ]

    list3 = []
    s = expl.get_raw(text)
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

