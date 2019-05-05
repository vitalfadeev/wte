# module wikoo

def find_first(s, lst, startpos=0):
    """
    Find in string 's', each item passed in list 'lst', and return nearest.
    
    in:  "{{name|arg1}}", ["{{", "|"]
    out: (0, "{{")
    
    in:  "{{name|arg1}}", ["}}", "|"]
    out: (6, "|")
    
    in:  "name", ["}}", "|"]
    out: (-1, None)
    """
    minpos = -1
    token = None
    
    for test in lst:
        pos = s.find(test, startpos)
        
        if pos != -1:
            if minpos == -1 or pos < minpos:
                minpos = pos
                token = test
                
    return (minpos, token)
    
assert find_first("{{abc}}", ["{{", "}}"]) == (0, "{{")
assert find_first("abc}}", ["{{", "}}"]) == (3, "}}")
assert find_first("abc", ["{{", "}}"]) == (-1, None)


def get_title_level(text, startpos=0):
    """
    Return sectin titile level.
    It count '='.
    
    in: "=== The title ==="
    out: 3
    """
    i = startpos
    l = len(text)
    
    while i < l and text[i] == "=":
        i += 1

    level = i - startpos
     
    return level

def find_title_end(text, level, startpos=0):
    """
    Find title end.
    It find '=' and test level.
    
    in:  "=== The title ==="
    out: 17
    
    in:  "=== The title"
    out: None
    """
    i = startpos
    l = len(text)
    
    while i < l:
        if text[i] == "=":
            # end, need check level
            end_level = get_title_level(text, i)
            if end_level == level:
                # OK
                return i + level # next char after last char
            else:
                # FAIL. levels not equal
                return None
            
        elif text[i] == "\n":
            # FAIL. EOL. title end not found
            return None
            
        else:
            i += 1
            
    return None # FAIL. end reached, title end not found


text = "=== The title ==="
level = get_title_level(text)
assert get_title_level(text) == 3
text = "=1="
assert get_title_level(text) == 1
text = "=== The title ==="
level = get_title_level(text)
assert find_title_end(text, level, level) == len(text)
text = "=== The title =="
level = get_title_level(text)
assert find_title_end(text, level, level) is None
text = "== The title ==="
level = get_title_level(text)
assert find_title_end(text, level, level) is None
text = "== The title"
level = get_title_level(text)
assert find_title_end(text, level, level) is None
text = "="
level = get_title_level(text)
assert find_title_end(text, level, level) is None

def parse_title(text, level, startpos, endpos):
    return text[startpos+level:endpos-level]

assert parse_title("=== 123 ===", get_title_level("=== 123 ==="), 0, len("=== 123 ===")) == " 123 "

class Title:
    """
    Class for storing section title. Like a ==English==
    """
    def __init__(self, title, level):
        self.title = title.strip()
        self.level = level
        self.parent = None
        
    def is_empty(self):
        """
        Check for this title is empty string.
        
        out: True | False
        """
        return len(self.title.strip()) == 0

    def __repr__(self):
        return "Title("+self.title+")"
        
        
def find_li_end(text, startpos=0):
    """
    Find end of the base of the list item.
    
    in:  "# list item text"
    out: 1
    
    in:  "### list item text"
    out: 3 
    """
    i = startpos
    l = len(text)
    
    while i < l:
        if text[i] in "#*:":
            i += 1
        else:
            break
            
    return i
        
assert find_li_end("#") == 1
assert find_li_end("#\n") == 1
assert find_li_end("# #\n") == 1
assert find_li_end("###\n") == 3

def parse_li(text, start, end):
    """
    Return list text from 'start' to 'end'.
    
    in:  "# list", 2, 6
    out: "list"
    """
    return text[start:end]

assert parse_li("# list", 0, len("# list")) == "# list"


class LI:
    """
    Class for storing list item. Like a '# list item text here'
    It contained child list items.
    
    Text:
      # item-1
      ## item-2
      # item-3
      
    Objects:
      LI(item 1)
        LI(item 2)
      LI(item 3)
    """
    def __init__(self, base):
        self.base = base
        self.childs = []
        self.data = []
        self.parent = None
        
    def find_lists(self):
        for child in self.childs:
            if isinstance(child, LI):
                yield child
        
    def is_empty(self):
        return self.base.strip() and all(d.is_empty() for d in self.data) and len(self.childs) == 0

    def add_child(self, child):
        child.parent = self
        self.childs.append(child)

    def add_data(self, item):
        item.parent = self
        self.data.append(item)

    def has_templates_only(self):
        """
        Check for list item contain Templates only. 
        Like a: # {{l|en|example}}
        
        for: # {{l|en|example}}
        out: True
        
        for: The text: # {{l|en|example}}
        out: False
        """
        for d in self.data:
            if isinstance(d, Template):
                # OK. has template
                continue
                
            elif isinstance(d, Text) and d.is_empty():
                # OK. ignore empty
                continue
                
            else:
                # FAIL. not Template and not empty
                return False
                
        # all OK
        return True
        
    def find_templates(self):
        """
        Find all templates from list item.
        
        for: # {{abc}}
        out: [Template(abc)]
        """
        for t in self.data:
            if isinstance(t, Template):
                yield t

    def get_text(self):
        """
        Return list item data in text form.
        """
        return self.base + "".join( [d.get_text() for d in self.data] )
        
    def __repr__(self):
        return "LI("+self.base+")"

def find_template_end(text, startpos=0):
    """
    in:  "{{123}}"
    out: 8
    
    in:  "{{123"
    out: None
    """    
    opened = 0
    closed = 0
    i = startpos
    l = len(text)
    lastclosed = i
    
    while i < l:
        (pos, token) = find_first(text, ["{{", "}}"], i)
        
        if pos == -1:
            # not found more
            i = l
            break
            
        else:
            # found
            # check what
            if token == "{{":
                opened += 1
                i = pos + 2
                
            elif token == "}}":
                closed += 1
                i = pos + 2
                lastclosed = i

                if opened == closed:
                    return i # OK.
                
            else:
                assert 0, "unsupported"

    if closed and opened > closed:
        return lastclosed # OK. template and bloken subtemplate inside
    else:
        return None # FAIL. broken template. without "}}"

assert find_template_end("{{abc}}") == 7
assert find_template_end("{{abc}} ") == 7
assert find_template_end("{{abc{{def}}}}") == 14
assert find_template_end("{{abc {def} }}") == 14
assert find_template_end("{{abc {def} }") is None
assert find_template_end("{{abc") is None
assert find_template_end("{{abc|{{sub} }}") == len("{{abc|{{sub} }}")


def get_template_inner(text, i, end):    
    """
    in:  "{{abc}}"
    out: abc
    """
    inner = text[i+2:end-2]
    return inner
    

class Template:
    """
    Class for storing template like a {{name|arg1|arg2}}.
    """
    def __init__(self, inner, name, args):
        self.inner = inner
        self.name = name
        self.args = args # {1=, 2=, lang=}
        self.parent = None
        self.childs = []
        
    def add_child(self, child):
        child.parent = self
        self.childs.append(child)
        
    def is_empty(self):
        return False
        
    def get_text(self):
        return ""
        
    def arg(self, key, default_value=None):
        """
        Return argument value.
        The 'key' can be 'int' or 'str'. 
        'int' - for positional arg. 
        'str' - for named arg.
        
        for: {{name|cat|cats}}
        in:  0
        out: "cat"
        
        for: {{name|cat|cats}}
        in:  1
        out: "cats"
        
        for: {{name|cat|cats|lang=en}}
        in:  "lang"
        out: "end"

        for: {{name|cat|cats}}
        in:  3
        out: None
        
        for: {{name|cat|cats}}
        in:  "lang"
        out: None        
        """
        a = self.args.get(key, None)
        
        if a is None:
            return default_value
        else:
            return a.as_string()
            
    def get_positional_args_count(self):
        """
        Return positional arguments count.
        
        for: {{name|cat|cats}}
        out: 2
        
        for: {{name}}
        out: 0
        
        for: {{name|lang=en}}
        out: 0
        """
        acount = 0
        
        for k,a in self.args.items():
            if not a.is_named():
                acount += 1
        
        return acount

    def __repr__(self):
        args = "|" + "|".join([repr(a) for a in self.args]) if self.args else ""
        return "Template("+self.name + args + ")"

def get_template_name(inner):
    """
    in:  "tname"
         "tname|a"
    out: tname
    """
    pos = inner.find("|")
    
    if pos == -1:
        return inner
    else:
        return inner[:pos]

class Arg:
    """
    Class for storing Arg.
    """
    def __init__(self, name, value, raw, endpos=None):
        self.name = name
        self.value = value
        self.raw = raw
        self.endpos = endpos
        
    def as_string(self):
        """
        Return value as string.
        
        for: {{noun|{{a}}}} - '{{a}}' is this current argument
        out: {{a}}
        
        for: {{noun|a}} - 'a' is this current argument
        out: a
        """
        return self.raw
        #return "".join(self.value)
        
    def as_list(self):
        return self.value
        
    def is_named(self):
        """
        Check for argument is named.
        
        out: Trhe | False
        """
        if isinstance(self.name, str) and not self.name.isnumeric():
            return True
        else:
            return False
        
    def __repr__(self):
        s = "".join([ repr(d) for d in self.value ]) if self.value else ""
        
        if self.is_named:
            s = self.name + "=" + s
            
        return "Arg(" + s + ")"

        
def get_template_arg(inner, startpos=0):
    """
    in:  "abc"
    out: Arg(abc)

    in:  "abc|a"
    out: Arg(abc)

    in:  ""
    out: None
    """
    i = startpos
    l = len(inner)
    
    strpos = startpos
    rawpos = startpos
    
    data = []
    
    # check is named
    eqpos = inner.find("=", i)
    if eqpos == -1:
        # positional
        name = None
    else:
        # = found
        # check name
        prob_name = inner[i:eqpos]
        
        if prob_name.strip().isalnum():
            # named
            name = prob_name.strip()
            i = eqpos + 1 #  i + len(name=)
            strpos = i
            rawpos = i
        else:
            # positional
            name = None
    
    # data
    while i < l:
        (pos, token) = find_first(inner, ["|", "{{"], i)
        
        if pos == -1:
            # no more
            i = l
            break
            
        elif token == "|":
            raw = inner[rawpos:pos]
            s = inner[strpos:pos]
            data.append(s)
            return Arg(name, data, raw, pos) # OK
            
        elif token == "{{":
            # sub template | just text
            end = find_template_end(inner, pos)
            
            if end is None:
                # not template
                # just text
                i = pos + 2
                continue
                
            else:
                # sub template
                subtemplate_inner = get_template_inner(inner, i, end)
                subt = parse_template(subtemplate_inner)
                data.append(subt)
                i = end
                strpos = end

    #
    if i == startpos:
        return None # FAIL. no args

    if strpos < i:
        # add tail str
        s = inner[strpos:]
        data.append(s)
        
    raw = inner[rawpos:]
        
    return Arg(name, data, raw, i) # OK. last arg
            

        ####
"""
        if inner[i] == "|":
            s = inner[strpos:i]
            data.append(s)
            return Arg(name, data, i) # OK
            
        elif inner.startswith("{{", i):
            # sub template | just text
            end = find_template_end(inner, i)
            
            if end is None:
                # just text
                i += 1
                
            else:
                # sub template
                subtemplate_inner = get_template_inner(inner, i, end)
                subt = parse_template(subtemplate_inner)
                data.append(subt)
                i = end
                strpos = end
            
        else:
            i += 1
    
    #
    if i == startpos:
        return None # FAIL. no args

    if strpos < i:
        # add tail str
        s = inner[strpos:]
        data.append(s)
        
    return Arg(name, data, i) # OK. last arg
"""

assert isinstance(get_template_arg("abc"), Arg)
assert get_template_arg("abc").value == ["abc"]
assert isinstance(get_template_arg("abc|a"), Arg)
assert get_template_arg("abc|a").value == ["abc"]
assert isinstance(get_template_arg("abc|a", 4), Arg)
assert get_template_arg("abc|a", 4).value == ["a"]
assert get_template_arg("abc|a", 6) is None
assert get_template_arg("abc").as_string() == "abc"
assert get_template_arg("k=v").is_named()
assert get_template_arg("k=v").name == "k"
assert get_template_arg("k=v").value == ["v"]
assert get_template_arg("k=v").as_string() == "v"
assert get_template_arg("a|{{a}}").as_string() == "a"

def parse_template(inner):
    """
    Parse string 'inner' and return Template object.
    
    for: "{{abc}}"
    in:  "abc"
    out: "Template(abc)"
    
    for: "{{abc|a}}"
    in:  "abc|a"
    out: "Template(abc, Arg(a))"
    """
    # template_inner
    # get name
    # get arg
    #   each arg:
    #     get name= 
    #       if names then is_named
    #     get value
    #       [str, "{{", "...", "}}"] - parse_template("{{", "...", "}}")
    #       [str, Template()]
    
    # name
    name = get_template_name(inner)
    
    # args
    i = len(name) + 1
    l = len(inner)
    args = {}
    acount = 0
    
    while i < l:
        a = get_template_arg(inner, i)
        
        if a.name is None:
            a.name = acount
            acount += 1
            
        args[a.name] = a
        i = a.endpos + 1
    
    return Template(inner, name, args)


assert get_template_arg("{{a}}").as_string() == "{{a}}"
assert get_template_arg("{{a}").as_string() == "{{a}"
assert get_template_arg("{{a {{b}}}}").as_string() == "{{a {{b}}}}"
assert get_template_arg("{{a|b}}").as_string() == "{{a|b}}"

assert isinstance(parse_template("abc"), Template)
assert len(parse_template("abc").args) == 0
assert isinstance(parse_template("abc|a"), Template)
assert parse_template("abc|a").args
assert isinstance(parse_template("abc|a").args[0], Arg)
assert parse_template("abc|a").args[0].value == ["a"]

assert len(parse_template("abc|a|b").args) == 2
assert isinstance(parse_template("abc|a|b").args[1], Arg)
assert parse_template("abc|a|b").args[1].value == ["b"]
assert len(parse_template("abc|a|b|").args) == 2


class CRLF:
    """
    Class for storing CRLF.
    """
    def __init__(self):
        self.childs = []
        self.parent = None
        
    def add_child(self, child):
        child.parent = self
        self.childs.append(child)
        
    def is_empty(self):
        return True

    def __repr__(self):
        return "CRLF"
        


def tokenize_text(text, startpos=0):
    """
    Parse string 'text' and generate tokens.
    It is generagor.
    
    in:  "==English==\n{{en-noun}}"
    out: [Section(English), Template(en-noun)]
    """
    # tokenize
    # =  - title,       find_title_end()    - if found: title
    #      section,     find_section_end()  - if found: section
    # #  - list_item,   find_li_end()       - if found: list_item
    # *  - list_item,   find_list_end()     - if found: list_item
    # {{ - template,    find_template_end() - if found: template
    #  
    # unnamed section
    # Section(title, childs)
    #   Section(title, childs)
    #     Template(name, args, childs)
    #     str
    #     LI(base, level, childs)
    #       str
    #       Template(name, args, childs)
    i = startpos
    l = len(text)
    string_start = i
    begin_of_line = True
    
    while i < l:
        if begin_of_line and text[i] == "=":
            begin_of_line = False
            
            # title
            if string_start != i:
                yield Text(text[string_start:i])

            #
            level = get_title_level(text, i)
            end = find_title_end(text, level, i+level)

            if end is None:
                # FAIL. no end. it is not title. it just string
                i += 1
            else:
                # OK
                title = parse_title(text, level, i, end)
                title = title.strip()
                # emit Title(title), emit Section(title)
                yield Title(title, level)
                i = end
                string_start = i                
            
        elif begin_of_line and text[i] == "#":
            begin_of_line = False

            # list item
            if string_start != i:
                yield Text(text[string_start:i])

            #
            end = find_li_end(text, i)
            base = parse_li(text, i, end)
            yield LI(base)
            i = end
            string_start = i
            
        elif begin_of_line and text[i] == "*":
            begin_of_line = False

            # list item
            if string_start != i:
                yield Text(text[string_start:i])

            #
            end = find_li_end(text, i)
            base = parse_li(text, i, end)
            yield LI(base)
            i = end
            string_start = i
                
        elif text.startswith("{{", i):
            begin_of_line = False

            # template
            if string_start != i:
                yield Text(text[string_start:i])

            #
            end = find_template_end(text, i)
            
            if end is None:
                # FAIL. broken template. it is the string
                i += 1
            else:
                # OK
                template_inner = get_template_inner(text, i, end)
                # parse recursive for subtemplates
                template = parse_template(template_inner)
                yield template
                i = end
                string_start = i
                
        elif text.startswith("\n", i):
            begin_of_line = True

            # template
            if string_start != i:
                yield Text(text[string_start:i])

            yield CRLF()
            i += 1
            string_start = i
            
        else:
            begin_of_line = False            
            i += 1

    # tail text
    if string_start != i:
        yield Text(text[string_start:])


class Section:
    """
    Class for storing section.
    """
    def __init__(self, title):
        self.title_object = title
        self.title = title.title
        self.level = title.level
        self.childs = []
        self.parent = None
        
    def is_empty(self):
        return len(self.title.strip()) == 0 and len(self.childs) == 0

    def add_child(self, child):
        child.parent = self
        self.childs.append(child)
        
    def find_lists(self):
        """
        Find LI objects in this section.
        
        for: 
             ==English==
             # item1
             # item2
        out: [LI(# item1), LI(# item2)]
        """
        for child in self.childs:
            if isinstance(child, LI):
                yield child
        
    def find_section(self, title, ignore_case=True):
        """
        Find Section object with the title 'title' in this section.
        
        for: 
             ==English==
             ===Noun===
        in: "Noun"
        out: [Section(Noun)]
        
        for: 
             ==English==
             ===Noun===
             ===Noun===
        in: "Noun"
        out: [Section(Noun), Section(Noun)]
        """
        if ignore_case:
            title = title.lower()
    
        for child in self.childs:
            if isinstance(child, Section):
                if (ignore_case and child.title.lower() == title) or (child.title == title):
                    yield child
        
        return None
        
    def find_section_recursive(self, title, ignore_case=True):
        """
        Find Section object with the title 'title' in this section and all subsections. Recursive.
        
        for: 
             ==English==
             ===Etymology===
             ====Noun====
        in: "Noun"
        out: [Section(Noun)]
        
        for: 
             ==English==
             ===Etymology===
             ====Noun====
             ====Noun====
        in: "Noun"
        out: [Section(Noun), Section(Noun)]
        """
        if ignore_case:
            title = title.lower()

        # check childs
        for child in self.childs:
            if isinstance(child, Section):
                # check title
                if ignore_case:
                    # case insense
                    if child.title.lower() == title:
                        yield  child
                else:
                    # case sense
                    if child.title == title:
                        yield  child

        # recursive. in width
        for child in self.childs:
            if isinstance(child, Section):
                for subsec in child.find_section_recursive(title, ignore_case):
                    yield subsec
        
    def find_sections(self, titles, ignore_case=True):
        """
        Find Section object with the on of title in 'titles' list. In this section.
        
        for: 
             ==English==
             ===Noun===
             ===Verb===
        in: ["Noun", "Verb"]
        out: [Section(Noun), Section(Verb)]
        
        for: 
             ==English==
             ===Noun===
             ===Noun===
             ===Verb===
        in: ["Noun", "Verb"]
        out: [Section(Noun), Section(Noun), Section(Verb)]
        """
        assert isinstance(titles, (list, tuple)), "titles must be list ot tuple"
        
        if ignore_case:
            titles = [t.lower() for t in titles]

        for child in self.childs:
            if isinstance(child, Section):
                if ignore_case:
                    # witout case
                    if child.title.lower() in titles:
                        yield child
                else:
                    # with case
                    if child.title in titles:
                        yield child
        
        return None
        
    def find_sections_recursive(self, titles, ignore_case=True):
        """
        Find Section object with the on of title in 'titles' list. In this section and all subsections. Recursive.
        
        for: 
             ==English==
             ===Noun===
             ===Sub===
             ====Verb====
        in: ["Noun", "Verb"]
        out: [Section(Noun), Section(Verb)]
        
        for: 
             ==English==
             ===Sub===
             ====Noun====
             ====Noun====
             ====Verb====
        in: ["Noun", "Verb"]
        out: [Section(Noun), Section(Noun), Section(Verb)]
        """
        assert isinstance(titles, (list, tuple)), "titles must be list ot tuple"

        if ignore_case:
            titles = list(map(str.lower, titles))

        # check childs
        for child in self.childs:
            if isinstance(child, Section):
                # check title
                if ignore_case:
                    # case insense
                    if child.title.lower() in titles:
                        yield  child
                else:
                    # case sense
                    if child.title in titles:
                        yield  child

        # recursive. in width
        for child in self.childs:
            if isinstance(child, Section):
                for subsec in child.find_sections_recursive(titles, ignore_case):
                    yield subsec
        
    def find_templates(self):
        """
        Find templates in this section.
        
        for:
            ==English==
            {{en-noun}}
            {{l|en|this}}
        out: [Template(en-noun), Template(l)]
        """
        for child in self.childs:
            if isinstance(child, Template):
                yield child

    def find_templates_recursive(self, startfrom=None):
        """
        Find templates in this section and in all subsections. Recursive.
        In LI (list items) searched also.
        
        for:
            ==English==
            ===Noun===
            {{en-noun}}
            {{l|en|this}}
        out: [Template(en-noun), Template(l)]
        """
        if startfrom is None:
            startfrom = self
        
        for child in startfrom.childs:
            if isinstance(child, Template):
                yield child

            if hasattr(child, "childs"):
                for c in self.find_templates_recursive(child):
                    yield c
                    
        # LI patch
        if isinstance(startfrom, LI):
            for child in startfrom.data:
                if isinstance(child, Template):
                    yield child

    def find_templates_recursive_no_subsections(self, startfrom=None):
        """
        Find templates in this section and in all subsections. Recursive.
        In LI (list items) searched also.
        
        for:
            ==English==
            ===Noun===
            {{en-noun}}
            {{l|en|this}}
        out: [Template(en-noun), Template(l)]
        """
        if startfrom is None:
            startfrom = self
        
        for child in startfrom.childs:
            if isinstance(child, Template):
                yield child

            if not isinstance(child , Section):
                if hasattr(child, "childs"):
                    for c in self.find_templates_recursive_no_subsections(child):
                        yield c
                    
        # LI patch
        if isinstance(startfrom, LI):
            for child in startfrom.data:
                if isinstance(child, Template):
                    yield child


    def find_templates_in_parents(self):
        """
        Find templates in parents
        
        for:
           ==English==
           {{t|en|cat}}
           
           ===Noun===
           {{t|en|cat2}}
           
        self: Section(Noun)
        out: [Template(cat)]
        """
        
        parent = self.parent
        
        while parent:
            if isinstance(parent, Section):
                for t in parent.find_templates_recursive_no_subsections():
                    yield t
                    
            parent = parent.parent
    

    def find_objects(self, types):
        """
        Find all object of type 'type'
        
        in:  [(Template, LI)]
        out: [Template(en-noun), Template(l), LI(# item1)]
        """
        for obj in self.childs:
            if isinstance(obj, types):
                yield obj

    def find_objects_between_templates(self, template1, template2, arg1=None):
        """
        Find all objects between template 'template1' and 'template2'.
        Optional check forst argument of template1 'arg1'.

        for:
            {{rel-top|related terms}}
            * {{l|en|knight}}, {{l|en|cavalier}}, {{l|en|cavalry}}, {{l|en|chivalry}}
            * {{l|en|equid}}, {{l|en|equine}}
            * {{l|en|gee}}, {{l|en|haw}}, {{l|en|giddy-up}}, {{l|en|whoa}}
            * {{l|en|hoof}}, {{l|en|mane}}, {{l|en|tail}}, {{l|en|withers}}
            {{rel-bottom}}
        out: [LI(), Template(l), Template(l), ...]
        """
        # {{rel-top|related terms}}
        # * {{l|en|knight}}, {{l|en|cavalier}}, {{l|en|cavalry}}, {{l|en|chivalry}}
        # * {{l|en|equid}}, {{l|en|equine}}
        # * {{l|en|gee}}, {{l|en|haw}}, {{l|en|giddy-up}}, {{l|en|whoa}}
        # * {{l|en|hoof}}, {{l|en|mane}}, {{l|en|tail}}, {{l|en|withers}}
        # {{rel-bottom}}
        generator = (c for c in self.childs)

        for c in generator:
            #if isinstance(c, Template):
            #    print(c)
            if isinstance(c, Template) and c.name == template1:
                # FOUND Template 1
                # check arg1
                if arg1 is None  or  len(c.args) >= 1  and c.args[0].as_string() == arg1:
                    pass # OK
                else:
                    continue # skip
                    
                # find objects
                for obj in generator:
                    if isinstance(obj, Template) and obj.name == template2:
                        # END. FOUND Template 2
                        break
                    else:
                        yield obj
                        
                # first block only
                break

    def find_objects_between_templates_recursive(self, template1, template2, arg1=None):
        """
        Recursive version of the [find_objects_between_templates()]
        """
        for c in self.childs:
            if isinstance(c, Section):
                for o in c.find_objects_between_templates(template1, template2, arg1):
                    yield o

                # recurse
                for o in c.find_objects_between_templates_recursive(template1, template2, arg1):
                    yield o
    
    def __repr__(self):
        return "Section(" + repr(self.title) + ")"
    

class Text:
    """
    Class for storing text.
    """
    def __init__(self, s):
        assert not isinstance(s, Text)
        self.s = s
        self.childs = []
        self.parent = None    
        
    def is_empty(self):
        if len(self.s.strip()) == 0:
            if all([c.is_empty() for c in self.childs]):
                return True
        
        return False
        
    def add_child(self, child):
        child.parent = self
        self.childs.append(child)
        
    def get_text(self):
        """
        Retrun raw text of this source.
        """
        return self.s
        #return "".join( [repr(c) for c in self.childs] )

    def __repr__(self):
        return "Text(" + self.s.replace("\n", "\\n") + ")"


def find_li_end_tokenized(li, generator):
    parent = li

    for t in generator:
    
        if isinstance(t, CRLF):
            # li end
            #li.add_data( t )
            break

        elif isinstance(t, Template):
            # Template
            #print("TEMPLATE:", parent)
            li.add_data( t )
            
        elif isinstance(t, Text):
            # text
            # go to container: Section
            li.add_data( t )
            
        else:
            assert 0, "unsupported"
        
    return li
    

def parse(text):
    """
    Parse text 'text' and return object tree.
    
    in:  text
    out: <Section>
    """
    root = Section(Title("", 0))
    parent = root
    generator = tokenize_text(text)

    for t in generator:
        # Section 
        #  Section
        #    Text
        #    Template
        #    Text
        #    List
        #      LI
        #      LI
        #      LI
        #    Text
        
        if isinstance(t, Title):
            # title, section
            section = Section(t)
                
            # select section
            while not isinstance(parent, Section):
                parent = parent.parent
                
            # select parent section
            while parent.level >= section.level:
                parent = parent.parent
                
            # create
            parent.add_child( section )
            
            #
            parent = section
            
        elif isinstance(t, LI):
            t = find_li_end_tokenized(t, generator)

            # List            
            if isinstance(parent, LI):
                # in list
                if t.base == parent.base:
                    # in same level
                    parent.parent.add_child( t )
                    parent = t
                    
                else:
                    # different levels
                    if t.base.startswith( parent.base ):
                        # the child
                        # new sub list
                        parent.add_child( t )
                        parent = t
                        
                    else:
                        # the parent
                        # find parent
                        while isinstance(parent, LI) and not t.base.startswith( parent.base ):
                            parent = parent.parent
                            
                        if isinstance(parent, LI) and t.base.startswith( parent.base ):
                            parent = parent.parent
                            
                        parent.add_child( t )
                        parent = t
                
            else:
                # new list
                # go to container: Section | LI
                while parent and not isinstance(parent, (Section, LI)):
                    parent = parent.parent
                
                parent.add_child( t )
                parent = t              
        
        elif isinstance(t, Template):
            # Template
            while not isinstance(parent, (Section, Text)):
                parent = parent.parent
            
            parent.add_child( t )
            parent = t
            
        elif isinstance(t, Text):
            # text
            # go to container: Section
            while parent and not isinstance(parent, Section):
                parent = parent.parent
                
            parent.add_child( t )
            parent = t
            
        elif isinstance(t, CRLF):
            # text
            pass
            
        else:
            assert 0, "unsupported"

    return root


def dump_section(sec, level=0, show_sections_only=None):
    """
    Print formatted tree of object 'sec'
    """
    #print( "  "*level, type(sec) )
    if show_sections_only is not None:
        if show_sections_only and isinstance(sec, Section):
            print( "  "*level, repr(sec).replace("\n", "") )
    else:
        print( "  "*level, repr(sec).replace("\n", "") )
    
    for child in sec.childs:
        dump_section( child, level + 1, show_sections_only )
