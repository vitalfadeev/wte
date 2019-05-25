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

import xml.parsers.expat
import re

from loggers import log, log_non_english, log_no_words, log_unsupported
from helpers import get_contents, is_ascii


wiki_entities = {
    "&nbsp;"    : " ",
    "&eacute;"  : "É",
    "&iquest;"  : "¿",
    "&iexcl;"   : "¡",
    "&laquo;"   : "«",
    "&raquo;"   : "»",
    "&lsaquo;"  : "‹",
    "&rsaquo;"  : "›",
}


class Context:
    label = ""
    tag = ""
    attr = ""
    

class Container:
    def __init__(self):
        self.name = ""
        self.childs = []
        self.parent = None
        self.raw = ""

    def add_child(self, child):
        # add. keep ordered
        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self

        self.childs.append(child)

    def remove_child(self, child):
        try: self.childs.remove(child)
        except ValueError: pass
        
    def add_cdata(self, s):
        if self.childs and isinstance(self.childs[-1], String): 
            self.childs[-1].raw += s
        else: 
            self.add_child( String(s) )

    def get_text(self):
        return " ".join( c.get_text() for c in self.childs )

    def get_raw(self):
        return self.raw

    def find_objects(self, cls, recursive=False, exclude=None):
        for c in self.childs:
            if isinstance(c, cls):
                if exclude is None or not isinstance(c, exclude):
                    yield c

            if recursive:
                if exclude is None or not isinstance(c, exclude):
                    for obj in c.find_objects(cls, recursive):
                        yield obj

    def find_section(self, name, recursive=False):
        for section in self.find_objects(Section, recursive):
            if section.has_name(name):
                yield section

    def find_top_objects(self, cls, callback):
        for c in self.childs:
            is_found = False
            
            if isinstance(c, cls):
                if callback(c):
                    is_found = True
                    yield c

            if not is_found:
                for obj in c.find_top_objects(cls, callback):
                    yield obj

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

    def __repr__(self):
        return "Container()"


class Article(Container):
    def __repr__(self):
        return "Article()"


class Template(Container):
    def args(self):
        for a in self.find_objects(Arg):
            yield a

    def arg(self, pos):
        args = list( self.args() )

        if isinstance(pos, int):
            # positional arg
            if pos < len(args):
                # OK
                return args[pos].get_value()
            else:
                # FAIL
                return None

        elif isinstance(pos, str):
            # named arg
            for a in args:
                if a.get_name() == pos:
                    # OK
                    return a.get_value()
            else:
                # FAIL
                return None

        else:
            assert 0, "unsupported"

    def get_text(self):
        # extract template
        #items = [self.name] + [ a.get_text() for a in self.args() ]
        #return "{{" + "|".join( items ) + "}}"
        s = self.arg(1)
        if s is None:
            s = self.arg(0)
        if s is None:
            s = ""
        return s

    def __repr__(self):
        return "Template(" + self.name + ")"


class String(Container):
    def __init__(self, raw=""):
        super().__init__()
        self.raw = raw

    def get_text(self):
        return self.raw

    def __repr__(self):
        return "String('" + self.raw.replace("\n", "\\n") + "')"

class Html(Container):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.attrs = []

    def get_text(self):
        return "".join( c.get_text() for c in self.childs )

    def __repr__(self):
        return "Html("+self.name+", "+repr(self.attrs)+")"


class Preformatted(Container):
    def __repr__(self):
        return "Preformatted()"

class Link(Container):
    def __repr__(self):
        return "Link()"

class Table(Container):
    def __repr__(self):
        return "Table()"

class Italic(Container):
    def __repr__(self):
        return "Italic()"

class Bold(Container):
    def __repr__(self):
        return "Bold()"

class Header(Container):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.level = 0

    def __repr__(self):
        return "Header(" + self.get_text() + ")"

# class H1(Header):
    # def __repr__(self):
        # return "H1(" + self.get_text() + ")"

# class H2(Header):
    # def __repr__(self):
        # return "H2(" + self.get_text() + ")"

# class H3(Header):
    # def __repr__(self):
        # return "H3(" + self.get_text() + ")"

# class H4(Header):
    # def __repr__(self):
        # return "H4(" + self.get_text() + ")"

# class H5(Header):
    # def __repr__(self):
        # return "H5(" + self.get_text() + ")"

# class H6(Header):
    # def __repr__(self):
        # return "H6(" + self.get_text() + ")"

# class H7(Header):
    # def __repr__(self):
        # return "H7(" + self.get_text() + ")"

class Comment(Container):
    def __repr__(self):
        return "Comment()"

class Li(Container):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.level = 0
        self.base = ""

    def get_text(self):
        return "".join( c.get_text() for c in self.childs if not isinstance(c, Li) )

    def __repr__(self):
        s = self.raw
        if len(s) > 24:
            s = s[:24] + "..."
        return "Li(" + s.replace("\n", "\\n") + ")"

class LiOrdered(Li):
    def __repr__(self):
        return "LiOrdered()"

class LiUnordered(Li):
    def __repr__(self):
        return "LiUnordered()"

class Section(Container):
    def __init__(self, *args, **kvars):
        super().__init__(*args, **kvars)
        self.level = 0
        self.header = None
        self.name = ""
        
    def has_name(self, expected_name, expected_lang=None):
        # case 1: .name
        if self.name == expected_name:
            return True
            
        # case 2: templated
        if self.header:
            for t in self.header.find_objects(Template, recursive=True):
                # case 2.1: {{expected_name}}
                if t.name == expected_name:
                    return True
                    
                # case 2.2: {{s|expected_name}}
                a1 = t.arg(0)
                if a1 and a1.strip().slower() == expected_name:
                    # test lang
                    if expected_lang:
                        lang = t.arg(1)
                        if lang is None:
                            return True
                        else:
                            if lang == expected_lang:
                                return True        
        return False

    def __repr__(self):
        return "Section(" + self.name + ", level:" + str(self.level) + ")"

class Arg(Container):
    def get_name(self):
        text = self.get_text()
        eqpos = text.find("=")

        if eqpos != -1:
            return text[:eqpos].strip()
        else:
            return None

    def get_value(self):
        text = self.get_text()
        eqpos = text.find("=")

        if eqpos != -1:
            return text[eqpos+1:].strip()
        else:
            return text.strip("\n")

    def __repr__(self):
        s = self.get_name()
        if s is None:
            s = self.get_text()
        if len(s) > 24:
            s = s[:24] + "..."
        return "Arg(" + s + ")"


class Mined(Container):
    def __init__(self, key, data, source, *args, **kvars):
        super().__init__(*args, **kvars)
        self.key = key, data, source
        self.data = data
        self.source = source

    def __repr__(self):
        s = repr(self.key) + ": " + repr(self.data)
        if len(s) > 60:
            s = s[:60] + "..."
        return "Mined(" + s + ")"    


def dump(root, level=0, types=None):
    #print( "  "*level, root, ":", root.raw.replace("\n", "\\n"))
    print( "  "*level, root, ":")
    #print( "  "*level, root, ":", root.get_text().replace("\n", "\\n"))

    for child in root.childs:
        if types and isinstance(child, types):
            dump(child, level+1, types)

def dump_sections(root, level=0):
    dump(root, level=0, types=(Section))

##### Comment #####
def find_comment_end(text, spos):
    pos = text.find("-->", spos)
    if pos != -1:
        return pos + len("-->")
    else:
        return len(text)


##### Quoted strings #####
def read_dq_string(text, spos):
    i = spos
    
    if text[i] == '"':
        i += 1
        
        pos = text.find("\"", i)
        
        while pos != -1:
            if pos > 0 and text[pos-1] != '\\':
                epos = pos+1
                return epos # OK
                
            pos = text.find("\"", pos + 1)
        
    return None

assert read_dq_string('"abc"', 0) == len('"abc"')


def read_sq_string(text, spos):
    i = spos
    
    if text[i] == '\'':
        i += 1
        
        pos = text.find('\'', i)
        
        while pos != -1:
            if pos > 0 and text[pos-1] != '\\':
                epos = pos+1
                return epos # OK
                
            pos = text.find('\'', pos + 1)
        
    return None

assert read_sq_string("'abc'", 0) == len("'abc'")


class NotName(Exception): None
class NotEQ(Exception): None
class NotAttribute(Exception): None
class NotTag(Exception): None
class NotFoundClosedTag(Exception): None
class NotHtml(Exception): None
class NotTemplate(Exception): None
class NotTemplateName(Exception): None
class NotTemplateArg(Exception): None
class NotParsed(Exception): None
class NotComment(Exception): None
class NotLink(Exception): None
class NotLinkArg(Exception): None
class NotHeader(Exception): None
class NotList(Exception): None


###### HTML parsing ######
def read_html_attr_name(text, spos):
    i = spos
    l = len(text)
    c = text[i]
    
    if c.isalpha() and is_ascii(text[i]):
        i += 1
        
        while i < l:
            c = text[i]
            
            if c.isalnum() and is_ascii(text[i]):
                i += 1
                
            elif c == '=':
                return i # OK
                
            elif c == ' ':
                return i # OK
        
            elif c == '>':
                return i # OK
        
            elif text.startswith("/>", i):
                return i # OK
                
            else:
                raise NotName()
                return i # FAIL
                
        return i # OK. end reached
        
    raise NotName()
    return i # FAIL

assert read_html_attr_name('name="value"', 0) == 'name="value"'.find("=")
assert read_html_attr_name('name = "value"', 0) == 'name = "value"'.find(" ")
assert 'name = "value"'[0:read_html_attr_name('name = "value"', 0)] == "name"
try: read_html_attr_name('"value"', 0)
except NotName: pass
try: read_html_attr_name('2', 0)
except NotName: pass


def read_html_attr_eq(text, spos):
    i = spos
    l = len(text)

    if i < l:
        if text[i] == '=':
            return i + 1 # OK
            
    raise NotEQ()
    return None # FAIL

assert read_html_attr_eq('=', 0) == len('=')

try: read_html_attr_eq(' ', 0)
except NotEQ: pass

try: read_html_attr_eq(' = ', 0)
except NotEQ: pass

try: read_html_attr_eq('a', 0)
except NotEQ: pass


def read_html_attr_spaces(text, spos):
    i = spos
    l = len(text)
    
    while i < l:
        if text[i] == ' ':
            i += 1 # OK
        else:
            break # OK
    
    return i # OK

assert read_html_attr_spaces(' ', 0) == len(' ')
assert read_html_attr_spaces(' = ', 0) == len(' ')
assert read_html_attr_spaces('', 0) == len('')


def read_html_attr_value(text, spos):
    i = spos
    l = len(text)
    
    while i < l:
        c = text[i]
        
        if c == '"':                
            epos = read_dq_string(text, i)
            
            # fix
            if Context.label == "manas" and Context.tag == "td" and Context.attr == "style":
                tdepos = text.find("</td>", i)
                if tdepos != -1:
                    epos = tdepos
                
            return epos # OK
        
        elif c == "'":
            epos = read_sq_string(text, i)
            return epos # OK
        
        elif c == ' ':
            return i # OK
    
        elif c == '>':
            return i # OK
    
        elif text.startswith('/>', i):
            return i # OK
    
        else:
            i += 1
    
    return i # OK

assert read_html_attr_value('123', 0) == len('123')
assert read_html_attr_value('"123"', 0) == len('"123"')
assert read_html_attr_value('\'123\'', 0) == len('\'123\'')
assert read_html_attr_value('123 ', 0)== len('123')
assert read_html_attr_value('"123', 0) is None
assert read_html_attr_value('123"', 0) is None

    
def read_html_tag_attribute(text, spos):
    i = spos
    l = len(text)
    
    while i < l:
        c = text[i]
        
        if c.isalnum() and is_ascii(c):
            # attr name
            try: epos = read_html_attr_name(text, i)
            except NotName: break
            aname = text[i:epos]
            Context.attr = aname
            
            # skip spaces
            epos = read_html_attr_spaces(text, epos)
            
            # =
            try: epos = read_html_attr_eq(text, epos)
            except NotEQ: return (epos, aname, None)
            eq = text[i:epos]
            
            # skip spaces
            epos = read_html_attr_spaces(text, epos)
            
            # attr value
            vpos = epos
            epos = read_html_attr_value(text, epos)
            avalue = text[vpos:epos]
            
            return (epos, aname, avalue)
            
        else:
            break
        
    raise NotAttribute()
    return None

assert read_html_tag_attribute("a = 123 ", 0) == (len("a = 123"), "a", "123") 
assert read_html_tag_attribute("a=123 ", 0) == (len("a=123"), "a", "123") 
assert read_html_tag_attribute("a= 123 ", 0) == (len("a= 123"), "a", "123") 
assert read_html_tag_attribute("a", 0) == (len("a"), "a", None) 
#assert read_html_tag_attribute("a=", 0) == (len("a="), "a", '') 
assert read_html_tag_attribute("a='asd'", 0) == (len("a='asd'"), "a", "'asd'") 
assert read_html_tag_attribute("a=\"asd\"", 0) == (len("a=\"asd\""), "a", "\"asd\"") 

try: read_html_tag_attribute("1=a", 0)
except NotAttribute: pass

try: read_html_tag_attribute(">=a", 0)
except NotAttribute: pass

try: read_html_tag_attribute("<=a", 0)
except NotAttribute: pass

                
def read_html_tag_attributes(text, spos):
    i = spos
    l = len(text)
    
    attrs = []
    
    while i < l:
        c = text[i]
        
        try: 
            (epos, aname, avalue) = read_html_tag_attribute(text, i)
            attrs.append( (epos, aname, avalue) )
            epos = read_html_attr_spaces(text, epos)
            i = epos
        except:
            break
        
    epos = i
    
    return (epos, attrs)
                
#assert read_html_tag_attributes("a = 123 ", 0) == (len("a = 123"), [(len("a = 123"), "a", "123")])
#assert read_html_tag_attributes("a=1 b=2", 0) == (len("a=1 b=2"), [(len("a=1"), "a", "1"), (len("a=1 b=2"), "b", "2")])
#assert read_html_tag_attributes("a=1 b", 0) == (len("a=1 b"), [(len("a=1"), "a", "1"), (len("a=1 b"), "b", None)])
#assert read_html_tag_attributes("a=1 1", 0) == (len("a=1 "), [(len("a=1"), "a", "1")])
#assert read_html_tag_attributes("a=1 >", 0) == (len("a=1 "), [(len("a=1"), "a", "1")])


def read_html_tag_name(text, spos):
    i = spos
    l = len(text)

    while i < l:
        c = text[i]
        
        if text[i].isalpha() and is_ascii(text[i]):
            # first alpha only
            i += 1
            
            while i < l:
                c = text[i]
                
                if c.isalnum() and is_ascii(c):
                    # alplha or numbers
                    i += 1
                    
                elif c == ' ':
                    return i # OK
                    
                elif c == '>':
                    return i # OK
                    
                elif text.startswith('/>', i):
                    return i # OK
                    
                else:
                    raise NotTag() # FAIL        
                    
        else:
            raise NotTag() # FAIL        
    
    return i # OK
    
assert read_html_tag_name("link>", 0) == len("link")
assert read_html_tag_name("link", 0) == len("link")
assert read_html_tag_name("link ", 0) == len("link")
assert read_html_tag_name("h1 ", 0) == len("h1")
assert read_html_tag_name("", 0) == len("")

try: read_html_tag_name("<link>", 0)
except NotTag: pass

try: read_html_tag_name("1", 0)
except NotTag: pass

try: read_html_tag_name("=", 0)
except NotTag: pass

try: read_html_tag_name(" ", 0)
except NotTag: pass

    
def read_html_tag(text, spos):
    i = spos
    l = len(text)
    
    log.debug("read_html_tag(): next block: %s", text[i:i+40])
    
    attrs = []
    
    if text[i] == "<":
        i += 1

        # tag name
        epos = read_html_tag_name(text, i)
        tag = text[i:epos]
        i = epos
        
        Context.tag = tag

        while i < l:
            c = text[i] 
            
            if c == " ":
                # skip spaces
                i += 1
                
            elif c.isalpha() and is_ascii(c):
                # read attrs
                (epos, attrs) = read_html_tag_attributes(text, i)
                if epos > i:
                    i = epos
                else:
                    i += 1
                
            elif c == '>':
                epos = i + len(">")
                is_self_closed = False
                return (epos, tag, attrs, is_self_closed) # OK
                
            elif text.startswith("/>", i):
                epos = i + len("/>")
                is_self_closed = True
                return (epos, tag, attrs, is_self_closed) # OK
                
            else:
                log.debug("read_html_tag(): non ascii symbol: %s: next block: %s", repr(c), repr(text[i:i+20]))
                raise NotTag() # FAIL
                
    raise NotTag() # FAIL


assert read_html_tag("<br>", 0) == (len("<br>"), "br", [], False)
assert read_html_tag("<br/>", 0) == (len("<br/>"), "br", [], True)
assert read_html_tag("<br />", 0) == (len("<br />"), "br", [], True)

try: read_html_tag("< br />", 0)
except NotTag: pass

assert read_html_tag("<br />", 0) == (len("<br />"), "br", [], True)
assert read_html_tag("<br clear=both/>", 0) == (len("<br clear=both/>"), "br", [(len("<br clear=both"), "clear", "both")], True)
assert read_html_tag("<br clear=\"both\"/>", 0) == (len("<br clear=\"both\"/>"), "br", [(len("<br clear=\"both\""), "clear", "\"both\"")], True)
assert read_html_tag("<br clear>", 0) == (len("<br clear>"), "br", [(len("<br clear"), "clear", None)], False)
assert read_html_tag("<br clear/>", 0) == (len("<br clear/>"), "br", [(len("<br clear"), "clear", None)], True)
assert read_html_tag("<br clear=>", 0) == (len("<br clear=>"), "br", [(len("<br clear="), "clear", "")], False)
assert read_html_tag("<br clear =>", 0) == (len("<br clear =>"), "br", [(len("<br clear ="), "clear", "")], False)

try: read_html_tag("<br clear=", 0)
except NotTag: pass

try: read_html_tag("<br clear", 0)
except NotTag: pass

try: read_html_tag("<неаски>", 0)
except NotTag: pass


def find_closed_tag(text, tag, spos):
    pos = text.find("</" + tag + ">", spos)

    if pos != -1:
        return pos
    else:
        raise NotFoundClosedTag()
    
assert find_closed_tag("<a> 123 </a>", "a", 0) == "<a> 123 </a>".find("</a>")

try: find_closed_tag("<a> 123 </a>", "b", 0)
except NotFoundClosedTag: pass


def read_html_comment(text, spos):
    i = spos
    l = len(text)
    
    if text.startswith("<!--", i):
        # strip comment
        epos = find_comment_end(text, i)
        comment = Comment()
        comment.raw = text[i:epos]
        return (epos, comment) # OK
    
    raise NotComment


def read_html(text, spos):
    i = spos
    l = len(text)
    
    if text[i] == "<":
        opened = []

        single_tags = ["br"]
        allowed_unclosed_tags = ["cite"]
        htmlobj = Container()
        current = htmlobj
        
        while i < l:            
            try:
                c = text[i]
                
                if text.startswith("<!--", i):
                    # strip comment
                    log.debug("read_html(): read_html_comment()")
                    (epos, comment) = read_html_comment(text, i)
                    i = epos
                    
                elif c == '<' and not text.startswith("</", i): # start tag <...>
                    # read tag
                    log.debug("read_html(): read_html_tag()")
                    (epos, tag, attrs, is_self_closed) = read_html_tag(text, i)
                    
                    obj = Html()
                    obj.name = tag.strip().lower()
                    obj.attrs = attrs
                    
                    current.add_child( obj )
                    
                    if tag in single_tags:
                        if len(opened) == 0:
                            htmlobj.epos = epos
                            return (epos, htmlobj.childs[0]) # OK
                        i = epos
                        
                    else:
                        current = obj
                        
                        # nowiki fix
                        if tag == "nowiki" and not is_self_closed:
                            epos2 = text.find("</nowiki>", epos)
                            if epos2 != -1:
                                current.add_cdata( text[epos:epos2] )
                                epos = epos2 + len("</nowiki>")
                                is_self_closed = True
                            else:
                                #assert 0, "<nowiki> without </nowiki>" 
                                raise NotHtml()

                        # code fix
                        if tag == "code" and not is_self_closed:
                            epos2 = text.find("</code>", epos)
                            if epos2 != -1:
                                current.add_cdata( text[epos:epos2] )
                                epos = epos2 + len("</code>")
                                is_self_closed = True
                            else:
                                assert 0, "<code> without </code>" 

                        # pre fix
                        if tag == "pre" and not is_self_closed:
                            epos2 = text.find("</pre>", epos)
                            if epos2 != -1:
                                current.add_cdata( text[epos:epos2] )
                                epos = epos2 + len("</pre>")
                                is_self_closed = True
                            else:
                                assert 0, "<pre> without </pre>" 

                        # self closed check
                        if is_self_closed:
                            if len(opened) == 0:
                                htmlobj.epos = epos
                                return (epos, htmlobj.childs[0]) # OK                        
                        else:
                            opened.append(tag)
                            
                        i = epos

                elif text.startswith("</", i): # close tag </...>
                    # read close tag
                    log.debug("read_html(): read_html_tag_name()")
                    epos = read_html_tag_name(text, i+len("</"))
                    
                    # spaces
                    epos = read_html_attr_spaces(text, epos)
                    
                    if text[epos] == '>':
                        tag = text[i+len("</"):epos]
                        
                        #if opened[-1] == tag: 
                        if tag in opened: 
                            opened.pop()
                            current = current.parent
                            
                            if len(opened) == 0:
                                epos += len(">")
                                htmlobj.epos = epos
                                return (epos, htmlobj.childs[0]) # OK
                            
                        else: 
                            log.error("opened: %s", repr(opened))
                            log.error("Closed tag '%s' without opened... [skip tag]", tag)

                            if len(opened) == 0:
                                #epos += len(">")
                                #htmlobj.epos = epos
                                #return (epos, htmlobj.childs[0]) # OK
                                raise NotTag() # FAIL
                            
                        i = epos + len('>')
                        
                    else:
                        raise NotTag() # FAIL
                    
                elif text.startswith('{{', i):
                    # read template
                    log.debug("read_html(): read_template()")
                    (epos, template) = read_template(text, i)
                    current.add_child( template )
                    i = epos
                    
                elif text.startswith('[[', i):
                    # read template
                    log.debug("read_html(): read_link()")
                    (epos, link) = read_link(text, i)
                    current.add_child( link )
                    i = epos
                    
                else:
                    # character data
                    current.add_cdata(c)
                    i += 1
                    
            except NotTag:
                # character data
                current.add_cdata(c)
                i += 1
                    
            except NotTemplate: 
                # character data
                current.add_cdata(c)
                i += 1
                
            except NotLink: 
                # character data
                current.add_cdata(c)
                i += 1
                
            except NotComment: 
                # character data
                current.add_cdata(c)
                i += 1
                
    raise NotHtml() # FAIL

assert isinstance( read_html("<a></a>", 0), tuple )
assert read_html("<a></a>", 0)[0] == len("<a></a>")
assert isinstance(read_html("<a></a>", 0)[1], Html)
assert read_html("<a></a>", 0)[1].name == 'a'
assert read_html("<a>123</a>", 0)[1].get_text() == "123"
assert read_html("<a> 123 </a>", 0)[1].get_text() == " 123 "
assert read_html("<a><b>123</b></a>", 0)[1].get_text() == "123"
assert read_html("<a></a><b></b>", 0)[0] == len("<a></a>")

res = read_html("<outer> <a> 123 </a> <!--{{tpl}}--> <b> 456 </b> </outer>", 0)
assert res[0] == len("<outer> <a> 123 </a> <!--{{tpl}}--> <b> 456 </b> </outer>")
assert res[1].get_text() == "  123    456  "


###### Template parsing ######
def read_template_name(text, spos):
    i = spos
    l = len(text)
    
    while i < l:
        c = text[i]
        
        if c == '|':
            epos = i
            return epos # OK
            
        elif text.startswith('}}', i):
            epos = i
            return epos # OK
            
        else:
            i += 1
        
    raise NotTemplateName()


def read_template_arg(text, spos):
    i = spos
    l = len(text)
    
    arg = Arg()
    cdata = []
    
    while i < l:
        c = text[i]
        
        try: 
            if c == '|': # next arg 
                epos = i
                return (epos, arg) # OK
                
            elif text.startswith('}}', i): # end
                epos = i
                return (epos, arg) # OK
                
            elif text.startswith("<!--", i):
                # strip comment
                log.debug("read_template_arg(): read_html_comment()")
                (epos, comment) = read_html_comment(text, i)
                i = epos                

            elif c == '<': # html
                # read html
                log.debug("read_template_arg(): read_html()")
                (epos, html) = read_html(text, i)
                arg.add_child( html )
                i = epos
                
            elif text.startswith('{{', i): # subtemplate
                # read template
                log.debug("read_template_arg(): read_template()")
                (epos, template) = read_template(text, i)
                arg.add_child( template )
                i = epos
                
            elif text.startswith('[[', i): # link
                # read Link
                log.debug("read_template_arg(): read_link()")
                (epos, link) = read_link(text, i)
                arg.add_child( link)
                i = epos
                
            else:
                # cdata
                arg.add_cdata(c)
                i += 1
            
        except NotComment:
            # cdata
            arg.add_cdata(c)
            i += 1

        except NotTemplate:
            # cdata
            arg.add_cdata(c)
            i += 1

        except NotHtml: 
            # cdata
            arg.add_cdata(c)
            i += 1
            
    raise NotTemplateArg()

assert repr(read_template_arg("1|", 0)) == "(1, Arg(1))"
assert read_template_arg("1|", 0)[1].get_text() == "1"
assert repr(read_template_arg("1}}", 0)) == "(1, Arg(1))"
assert read_template_arg("1}}", 0)[1].get_text() == "1"
assert read_template_arg("<a>1</a>|", 0)[1].get_text() == "1"
assert read_template_arg("<a>|", 0)[1].get_text() == "<a>"

try: read_template_arg("1", 0)
except NotTemplateArg: pass


def read_template(text, spos):
    i = spos
    l = len(text)
    
    if text.startswith("{{", i):    
        i += len("{{")
        
        template = Template()

        # name
        try: 
            epos = read_template_name(text, i)
            name = text[i:epos]
            template.name = name.strip().lower()
                
            #
            while i < l:
                c = text[i]

                if c == '|':
                    i += 1
                    log.debug("read_template(): read_template_arg()")
                    (epos, arg) = read_template_arg(text, i)
                    template.add_child( arg )
                    i = epos
                    
                elif text.startswith('}}', i):
                    epos = i + len('}}')
                    template.raw = text[spos:epos]
                    return (epos, template) # OK
                
                else:
                    i += 1
                    
            raise NotTemplate # FAIL
                
        except NotTemplateName:
            raise NotTemplate # FAIL

        except NotTemplateArg:
            raise NotTemplate # FAIL

    raise NotTemplate # FAIL


res = read_html("<a>{{tpl}}</a>", 0)
#assert res[0] == len("<a>{{tpl}}</a>")
#assert res[1].get_text() == "{{tpl}}"
assert isinstance(res[1], Html)
assert isinstance(res[1].childs[0], Template)
assert res[1].childs[0].name == "tpl"

try: read_html("{{tpl}}", 0)
except NotHtml: pass

try: read_template("<a>{{tpl}}</a>", 0)
except NotTemplate: pass

assert read_template("{{tpl|<a></a>}}", 0)[0] == len("{{tpl|<a></a>}}")
assert isinstance(read_template("{{tpl|<a></a>}}", 0)[1], Template)
assert repr( read_template("{{tpl|<a></a>}}", 0) ) == "(15, Template(tpl))"


##### Link parsing #####
def read_link_arg(text, spos):
    i = spos
    l = len(text)
    
    arg = Arg()
    cdata = []
    
    while i < l:
        c = text[i]
        
        try: 
            if c == '|': # next arg 
                epos = i
                return (epos, arg) # OK
                
            elif text.startswith(']]', i): # end
                epos = i
                return (epos, arg) # OK
                
            elif text.startswith('{{', i): # subtemplate
                # read template
                (epos, template) = read_template(text, i)
                arg.add_child( template )
                i = epos
                
            elif text.startswith("<!--", i):
                # strip comment
                (epos, comment) = read_html_comment(text, i)
                i = epos                

            elif c == '<': # html
                # read html
                (epos, html) = read_html(text, i)
                arg.add_child( html )
                i = epos
                
            else:
                # cdata
                arg.add_cdata(c)
                i += 1
            
        except NotComment:
            # cdata
            arg.add_cdata(c)
            i += 1

        except NotTemplate:
            # cdata
            arg.add_cdata(c)
            i += 1

        except NotHtml: 
            # cdata
            arg.add_cdata(c)
            i += 1
            
    raise NotLinkArg()


def read_link(text, spos):
    i = spos
    l = len(text)
    
    if text.startswith("[[", i):    
        i += len("[[")
        
        link = Link()

        # name
        try: 
            while i < l:
                c = text[i]
                
                if c == '|':
                    i += 1
                    (epos, arg) = read_link_arg(text, i)
                    link.add_child( arg )
                    i = epos
                    
                elif text.startswith(']]', i):
                    epos = i + len(']]')
                    return (epos, link) # OK
                
                else:
                    (epos, arg) = read_link_arg(text, i)
                    link.add_child( arg )
                    i = epos
                    
            raise NotLink # FAIL
                
        except NotLinkArg:
            raise NotLink # FAIL

    raise NotLink # FAIL

assert repr(read_link("[[ ]]", 0)) == "(5, Link())"
assert read_link("[[ http://wikipedia.org/wiki/cat ]]", 0)[0] == len("[[ http://wikipedia.org/wiki/cat ]]")
assert read_link("[[ http://wikipedia.org/wiki/cat ]]", 0)[1].get_text() == " http://wikipedia.org/wiki/cat "
assert read_link("[[ http://wikipedia.org/wiki/cat | abc ]]", 0)[1].get_text() == " http://wikipedia.org/wiki/cat   abc "

try: read_html("<font size=4%></font size>", 0)
except NotHtml: pass


###### Header parsing ######
def read_header_level(text, spos):
    i = spos
    l = len(text)
    
    while i < l and text[i] == '=':
        i += 1
        
    epos = i
    level = i - spos
    
    return (epos, level)


def read_header(text, spos):
    i = spos
    l = len(text)
    
    if text.startswith("\n=", i):        
        i += len("\n")
        (epos, level) = read_header_level(text, i)

        header = Header()
        current = header
        header.level = level # level
        
        i = epos
        
        while i < l:
            c = text[i]
            
            try: 
                if c == '=':
                    (epos, level2) = read_header_level(text, i)
                    if level == level2:
                        header.name = header.get_text()
                        header.raw = text[spos:epos]
                        return (epos, header) # OK
                        
                    else:
                        # character data
                        current.add_cdata(c)
                        i += 1                    

                elif c == '\n':
                    raise NotHeader()

                elif text.startswith("<!--", i):
                    # strip comment
                    (epos, comment) = read_html_comment(text, i)
                    i = epos                
                    
                elif c == '<':
                    # HTML
                    (epos, html) = read_html(text, i)
                    current.add_child(html)
                    i = epos

                elif text.startswith('{{', i):
                    # Template
                    (epos, template) = read_template(text, i)
                    current.add_child(template)
                    i = epos
                
                elif text.startswith('[[', i):
                    # Link
                    (epos, link) = read_link(text, i)
                    current.add_child(link)
                    i = epos
                
                else:
                    # character data
                    current.add_cdata(c)
                    i += 1
                    
            except NotComment:
                # character data
                current.add_cdata(c)
                i += 1
            
            except NotHtml:
                # character data
                current.add_cdata(c)
                i += 1
            
            except NotTemplate:
                # character data
                current.add_cdata(c)
                i += 1
            
            except NotLink:
                # character data
                current.add_cdata(c)
                i += 1
                        
    raise NotHeader()


###### List parsing ######
def read_list_level(text, spos):
    i = spos
    l = len(text)
    
    while i < l and text[i] in "#*:":
        i += 1
        
    epos = i
    level = i - spos
    
    return (epos, level)


def read_list(text, spos):
    i = spos
    l = len(text)
    
    if text.startswith("\n#", i) or text.startswith("\n*", i) or text.startswith("\n:", i):
        i += len("\n")
        (epos, level) = read_list_level(text, i)

        li = Li()
        current = li
        li.level = level # level
        li.base = text[i:epos] # base
        
        i = epos
        
        while i < l:
            c = text[i]
            
            try: 
                if c == '\n':
                    # end of the list
                    epos = i
                    li.raw = text[spos+len("\n"):epos]
                    return (epos, li) # OK

                elif text.startswith("<!--", i):
                    # strip comment
                    log.debug("read_list(): read_html_comment()")
                    (epos, comment) = read_html_comment(text, i)
                    i = epos                
                    
                elif c == '<':
                    # HTML
                    log.debug("read_list(): read_html()")
                    (epos, html) = read_html(text, i)
                    current.add_child(html)
                    i = epos

                elif text.startswith('{{', i):
                    # Template
                    log.debug("read_list(): read_template()")
                    (epos, template) = read_template(text, i)
                    current.add_child(template)
                    i = epos
                
                elif text.startswith('[[', i):
                    # Link
                    log.debug("read_list(): read_link()")
                    (epos, link) = read_link(text, i)
                    current.add_child(link)
                    i = epos
                
                else:
                    # character data
                    current.add_cdata(c)
                    i += 1
                    
            except NotComment:
                # character data
                current.add_cdata(c)
                i += 1
            
            except NotHtml:
                # character data
                current.add_cdata(c)
                i += 1
            
            except NotTemplate:
                # character data
                current.add_cdata(c)
                i += 1
            
            except NotLink:
                # character data
                current.add_cdata(c)
                i += 1
    
            except NotList:
                # character data
                current.add_cdata(c)
                i += 1
    
        epos = i
        li.raw = text[spos+len("\n"):epos]
        return (epos, li)
        
    raise NotList()
    

###### Text parsing ######
def tagizer(text, spos=0):
    i = spos
    l = len(text)

    root = Section()
    current = root
        
    opened = []
    closed = []
    
    while i < l:
        c = text[i]
        #print(i, end="")
        #print(c.replace("\n", "\\n"), end="")

        try: 
            if text.startswith("<!--", i):
                # strip comment
                log.debug("read_html_comment()")
                (epos, comment) = read_html_comment(text, i)
                i = epos                
                
            elif c == '<':
                # HTML
                log.debug("read_html()")
                (epos, html) = read_html(text, i)
                current.add_child(html)
                i = epos

            elif text.startswith('{{', i):
                # Template
                log.debug("read_template()")
                (epos, template) = read_template(text, i)
                current.add_child(template)
                i = epos
            
            elif text.startswith('[[', i):
                # Link
                log.debug("read_link()")
                (epos, link) = read_link(text, i)
                current.add_child(link)
                i = epos
            
            elif text.startswith('\n=', i):
                # Header
                log.debug("read_header()")
                (epos, header) = read_header(text, i)
                current.add_child(header)
                i = epos
            
            elif text.startswith('\n#', i):
                # Li
                log.debug("read_list()")
                (epos, li) = read_list(text, i)
                current.add_child(li)
                i = epos
            
            elif text.startswith('\n*', i):
                # Li
                log.debug("read_list()")
                (epos, li) = read_list(text, i)
                current.add_child(li)
                i = epos
            
            elif text.startswith('\n:', i):
                # Li
                log.debug("read_list()")
                (epos, li) = read_list(text, i)
                current.add_child(li)
                i = epos
            
            else:
                # character data
                current.add_cdata(c)
                i += 1
                
        except NotComment:
            # character data
            current.add_cdata(c)
            i += 1
        
        except NotHtml:
            # character data
            current.add_cdata(c)
            i += 1
        
        except NotTemplate:
            # character data
            current.add_cdata(c)
            i += 1
        
        except NotLink:
            # character data
            current.add_cdata(c)
            i += 1
        
        except NotHeader:
            # character data
            current.add_cdata(c)
            i += 1
        
    epos = i
    return (epos, root) # OK
    #raise NotParsed # FAIL

assert repr(tagizer("<a>123</a>")) == "(10, Section(, level:0))"
assert tagizer("<a>123</a>")[1].get_text() == "123"
assert tagizer("<a> 123 </a>")[1].childs[0].childs[0].raw == " 123 "

res = tagizer("=={{-ru-}}==\n")
res = tagizer("=={{language|ru}}==\n")
res = tagizer("=={{language|{{-ru-|-r-}} }}==\n")
res = tagizer("{{language|{{-ru-|-r-}} }}\n")
res = tagizer("<!-- -->{{language|{{-ru-|<!-- -->}} }}\n")
res = tagizer("<!-- -->{{language|{{-ru-|<!-- [[ ]] -->}} }}\n")
res = tagizer("<!-- -->{{language|{{-ru-|<!-- [[ ]] -->}}| [[ http://wiki/get?a&b=1 ]] }}\n")

res = tagizer("\n==English==")
res = tagizer("\n=={{English}}==")
res = tagizer("\n=={{-ru-}}==")

res = tagizer("\n# list 1")
res = tagizer("\n* list 1")
res = tagizer("\n# list 1\n# list 2")
res = tagizer("\n# list 1{{t\n|en=\n|ru=}}\n# list 2")


# res = tagizer("""
# ## "<span title="he, she or it">it</span> is robbed, <span title=he, she or it">it</span> is stolen, it is plundered, <span title="he, she or it">it</span> is carried&nbsp;off"
# """)


def pack_lists(root):
    def is_child_li(parent, li):
        pa_base = parent.base
        li_base = li.base
        
        if li_base.startswith(pa_base):
            if li_base == pa_base:
                return False
            else:
                return True
        else:
            return False

    childs = root.childs.copy()
    parent = None
    
    for c in childs: # first li of the block
        if isinstance(c, Li):
            if parent is None:
                parent = c
                
            elif not isinstance(parent, Li):
                parent = c
                
            else:
                if is_child_li(parent, c):
                    parent.add_child(c)
                    parent = c
                    
                else:
                    while not is_child_li(parent, c):
                        parent = parent.parent
                        if not isinstance(parent, Li):
                            break
                        
                    if isinstance(parent, Li):
                        parent.add_child(c)
                        
                    parent = c
                    
    return root


res = tagizer("\n# list 1{{t\n|en=\n|ru=}}\n# list 2")
res = tagizer("\n# list 1{{t\n|en=\n|ru=}}\n## list 2\n##* list 2-1\n\n# list 3")
pack_lists( res[1] )

text = """
# An animal of the family [[Felidae]]:
#* {{quote-book|lang=en|year=2011|author=Karl Kruszelnicki|title=Brain Food|isbn=1466828129|page=53|passage=Mammals need two genes to make the taste receptor for sugar. Studies in various '''cats''' (tigers, cheetahs and domestic cats) showed that one of these genes has mutated and no longer works.}}
#: {{syn|en|felid}}
## A domesticated [[subspecies]] (''[[Felis silvestris catus]]'') of [[feline]] animal, commonly kept as a house [[pet]]. {{defdate|from 8<sup>th</sup>c.}}
##* {{RQ:WBsnt IvryGt|II}}
##*: At twilight in the summer there is never anybody to fearвЂ”man, woman, or '''cat'''вЂ”in the chambers and at that hour the mice come out. They do not eat parchment or foolscap or red tape, but they eat the luncheon crumbs.
##: {{syn|en|puss|pussy|malkin|kitty|pussy-cat|grimalkin|Thesaurus:cat}}
## Any similar animal of the family [[Felidae]], which includes [[lion]]s, [[tiger]]s, bobcats, etc.
##* '''1977''', Peter Hathaway Capstick, ''Death in the Long Grass: A Big Game Hunter's Adventures in the African Bush'', St. Martin's Press, 44.
##*: I grabbed it and ran over to the lion from behind, the '''cat''' still chewing thoughtfully on Silent's arm.
##* '''1985''' January, George Laycock, "Our American Lion", in Boy Scouts of America, ''Boy's Life'', 28.
##*: If you should someday round a corner on the hiking trail and come face to face with a mountain lion, you would probably never forget the mighty '''cat'''.
##* '''2014''', Dale Mayer, ''Rare Find. A Psychic Visions Novel'', Valley Publishing.
##*: She felt privileged to be here, living the experience inside the majestic '''cat''' [i.e. a tiger]; privileged to be part of their bond, even for only a few hours.
# A person:
## {{lb|en|offensive}} A spiteful or angry [[woman]]. {{defdate|from earlier 13<sup>th</sup>c.}}
##* '''1835''' September, anonymous, "The Pigs", in ''The New-England Magazine'', Vol. 9, 156.
##*: But, ere one rapid moon its tale has told, / He finds his prize вЂ” a '''cat''' вЂ” a slut вЂ” a scold.
##: {{syn|en|bitch}}
## An enthusiast or player of [[jazz]].
##* {{quote-song|lang=en|year=2008|author={{w|Nick Cave and the Bad Seeds}}|title=Hold on to Yourself|passage=I turn on the radio / There's some '''cat''' on the saxophone / Laying down a litany of excuses}}
## {{lb|en|slang}} A person (usually male).
##* {{quote-song
|lang=en
|title=Starman
|album=The Rise and Fall of Ziggy Stardust and the Spiders from Mars
|artist=David Bowie
|year=1972
|passage=Didn't know what time it was the lights were low / I leaned back on my radio / Some '''cat''' was layin' down some rock'n'roll 'lotta soul, he said}}
##* '''1973''' December, "Books Noted", discussing ''A Dialogue'' (by James Baldwin and Nikki Giovanni), in ''Black World'', Johnson Publishing Company, 77.
##*: BALDWIN: That's what we were talking about before. And by the way, you did not have to tell me that you think your father is a groovy '''cat'''; I knew that.
##* {{quote-song|lang=en|artist={{w|Shaquille O'Neal}}|title=Fiend|year=1998|album=Respect|passage=What fags are true I know what Mack's might do<br/>I'm quite familiar with '''cats''' like you<br>Provoke to get me give me a good reason to smoke me<br>Try to break me but never wrote me)}}
##* {{quote-song|lang=en|year=2006|lyricist=Masta Ace|title=Sick of it all|album=Pariah|passage=I am sick of rappers claiming they hot when they really not<br/>I am sick of rappers bragging about shit they ainвЂ™t really got<br/>These '''cats''' stay rapping about cars they donвЂ™t own<br/>I am sick of rappers bragging about models they donвЂ™t bone.[вЂ¦]<br/>And I am sick of all these '''cats''' with no talent<br/>That never lived in the hood but yet their lyrics be so violent.}}
##: {{syn|en|bloke|chap|cove|dude|fellow|fella|guy}}
## {{lb|en|slang}} A [[prostitute]]. {{defdate|from at least early 15<sup>th</sup>c.}}
##* '''1999''', Carl P. Eby, ''Hemingway's Fetishism. Psychoanalysis and the Mirror of Manhood'', State University of New York Press, 124.
##*: вЂњTell me. Willie said there was a '''cat''' in love with you. That isn't true, is it?вЂќ вЂњYes. It's true,вЂќ Hudson corrects her, letting her think that by вЂњcatвЂќ he means prostitute.
# {{lb|en|nautical}} A strong tackle used to hoist an anchor to the [[cathead]] of a ship.
#* '''2009''', Olof A. Eriksen, ''Constitution - All Sails Up and Flying'', Outskirts Press, 134.
#*: Overhaul down & hook the '''cat''', haul taut. Walk away the '''cat'''. When up, pass the '''cat''' head stopper. Hook the fish in & fish the anchor.
# {{lb|en|chiefly|nautical}} {{non-gloss definition|Short form of}} [[cat-o'-nine-tails]].
#* {{quote-book|lang=en|year=1839|section=testimony by {{w|Henry L. Pinckney}} (Assembly No. 335)|title=Documents of the Assembly of the State of New York|page=44|passage={{...}}he whipped a black man for disobedience of his orders fifty lashes; and again whipped him with a '''cat''', which he wound with wire, about the same number of stripes;{{...}}he used this '''cat''' on one other man, and then destroyed the '''cat''' wound with wire.}}
# {{lb|en|archaic}} A sturdy merchant sailing vessel {{qualifier|now only in "[[catboat]]"}}.
# {{lb|en|archaic|uncountable}} The game of "[[trap and ball]]" (also called "cat and dog").
## The trap of the game of "trap and ball".
# {{lb|en|archaic}} The pointed piece of wood that is struck in the game of [[tipcat]].
# {{lb|en|slang|vulgar|African American Vernacular English}} A [[vagina]], a [[vulva]]; the female external genitalia.
#* {{quote-book|lang=en|year=1969|author=Iceberg Slim|title=Pimp: The Story of My Life|publisher=Holloway House Publishing|passage="What the hell, so this broad's got a prematurely-gray '''cat'''."}}
#* {{quote-book|lang=en|year=2005|author=Carolyn Chambers Sanders|title=Sins & Secrets|publisher=Hachette Digital|passage=As she came up, she tried to put her '''cat''' in his face for some licking.}}
#* {{quote-book|lang=en|year=2007|author=Franklin White|title=Money for Good|publisher=Simon and Schuster|page=64|passage=I had a notion to walk over to her, rip her apron off, sling her housecoat open and put my finger inside her '''cat''' to see if she was wet or freshly fucked because the dream I had earlier was beginning to really annoy me.}}
# A [[double]] [[tripod]] (for holding a [[plate]], etc.) with six feet, of which three rest on the ground, in whatever position it is placed.
# {{lb|en|historical}} A [[wheel]]ed [[shelter]], used in the [[Middle Ages]] as a [[siege]] weapon to allow [[assailant]]s to approach enemy [[defence]]s.
#: {{syn|en|tortoise|Welsh cat}}

"""
res = tagizer(text, 0)
res = pack_lists( res[1] )
#dump( res, 0, (Section, Li) )
#exit(1)
#print( res )


def get_header_level(header):
    if isinstance(header, Header):
        return header.level
        
    elif isinstance(header, Html):
        if header.name == "h1":
            return 1
        elif header.name == "h2":
            return 2
        elif header.name == "h3":
            return 3
        elif header.name == "h4":
            return 4
        elif header.name == "h5":
            return 5
        elif header.name == "h6":
            return 6
        elif header.name == "h7":
            return 7

    else:
        assert 0, "unsupported header"


def pack_sections(root, section_templates=None):
    # build tree by levels

    # subsections
    top_section = root
    top_section.level = 0
    parent = top_section

    # walk over childs and put to new sections tree
    childs = root.childs.copy()
    generator = (c for c in childs)

    for e in generator:
        if isinstance(e, Header):
            header = e
        
            # find next same level or higher
            section = Section()
            section.level = get_header_level(header)
            section.header = header
            #section.name = header.get_text().strip().lower()
            section.name = header.get_raw().strip().strip('=').strip().lower()

            section.add_child(header)

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
        
        elif section_templates and isinstance(e, Template) and e.name in section_templates:
            header = e
        
            # find next same level or higher
            section = Section()
            section.level = 4 # hardcoded
            section.header = header
            #section.name = header.get_text().strip().lower()
            section.name = e.name

            section.add_child(header)

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
        
        else:
            parent.add_child(e)
            
        # recursive 
        pack_sections( e )
            
    # return new tree
    return top_section


res = tagizer("""
==English==
{{head}}

===Noun===
{{en-noun|s}}

====Translations====
{{t|ru|term}}

===Verb===
{{en-verb|s}}

""")
#dump( pack_sections( res[1] ) )

res = tagizer("""
=={{-ru-}}==
""")
#dump( pack_sections( res[1] ) )

def parse(text):
    (epos, tree) = tagizer(text)
    return tree
