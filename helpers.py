#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import io
import pickle
import json


def create_storage(folder_name):
    """
    Create folders recusively.

    In:
      folder_name: Storage folder name

    """
    if (not os.path.exists(folder_name)):
        os.makedirs(folder_name, exist_ok=True)


def sanitize_filename(filename):
    """
    Remove from string 'filename' all nonascii chars and  punctuations.
    """
    filename = str(filename)
    filename = "".join(x if x.isalnum() else "_" for x in filename)

    # fixes
    if filename.lower() == "con":
        filename = "reserved_con"

    elif filename.lower() == "aux":
        filename = "reserved_aux"

    elif filename.lower() == "prn":
        filename = "reserved_prn"

    return filename


def unique(lst):
    return list(set(lst))


def get_contents(filename):
    """
    Read the file 'filename' and return content.
    """
    with open(filename, 'rt', encoding="UTF-8") as f:
        return f.read()


def put_contents(filename, content):
    """
    Save 'content' to the file 'filename'. UTF-8.
    """
    with open(filename, "w", encoding="UTF-8") as f:
        f.write(content)

def save_to_pickle(treemap, filename):
    """
    Save Treemap to the 'filename' in Pickle format.

    In:
        treemap
        filename
    """
    create_storage(os.path.dirname(os.path.abspath(filename)))

    with open(filename, "wb") as f:
        pickle.dump(treemap, f)


def load_from_pickle(filename):
    """
    Load Treemap from the file 'filename'. File must be in Pickle format.

    In:
        filename
    Out:
        sorteddict
    """
    with open(filename, "rb") as f:
        obj = pickle.load(f, encoding="UTF-8")
        return obj

    return None


def proper(s):
    if len(s) == 0:
        return s
    elif len(s) == 1:
        return s[0].upper()
    else:
        return s[0].upper() + s[1:].lower()

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

def get_number(s):
    """
    in:  1a
    out: 1
    
    in:  10a
    out: 10
    """
    result = ""
    
    for c in s:
        if c.isnumeric():
            result += c
        else:
            break
            
    return result
    

def convert_to_alnum(s, replace_char="_"):
    return "".join( (c if c.isalnum() else replace_char for c in s ) )


def get_lognest_word(lst):
    longest = ""
    maxlen = 0

    for w in lst:
        if len(w) > maxlen:
            maxlen = len(w)
            longest = w

    return longest


def remove_comments(s, startpos=0):
    cs = s.find("<!--", startpos)
    
    if cs != -1:
        ce = s.find("-->", cs+len("<!--"))
        
        if ce != -1:
            cleaned = s[:cs] + s[ce+len("-->"):]
            return remove_comments(cleaned)
    
    return s
    
def extract_from_link(s, startpos=0):
    cs = s.find("[", startpos)
    
    if cs != -1:
        ce = s.find("]", cs+len("["))
        
        if ce != -1:
            cleaned = s[:cs] + s[cs+len("["):ce] + s[ce+len("]"):]
            return extract_from_link(cleaned)
    
    return s


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.
    """
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None
        def readable(self):
            return True
        def readinto(self, b):
            try:
                l = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0    # indicate EOF
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)



def is_ascii(s):
    return all(ord(c) < 128 for c in s)


class Store:
    templates = {}
    sections = {}
    counter = 0
    
def add_template(s, t):
    # add template
    lst = Store.sections.get(s.name, None)
    if lst is None:
        lst = []
        Store.sections[s.name] = lst
    if t.name not in lst:
        lst.append(t.name)
        lst.sort()
        
    # add section
    lst = Store.templates.get(t.name, None)
    if lst is None:
        lst = []
        Store.templates[t.name] = lst
    if s.name not in lst:
        lst.append(s.name)
        lst.sort()
    
    # periodically save
    if Store.counter > 100000:
        save()
        Store.counter = 0
        
    # update counter
    Store.counter += 1
        
def save():
    js = json.dumps(Store.templates, sort_keys=False, indent=4, ensure_ascii=False)
    put_contents("templates.json", js)
    
    js = json.dumps(Store.sections, sort_keys=False, indent=4, ensure_ascii=False)
    put_contents("sections.json", js)

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def check_flag(s, flags):
    for flag in flags:
        if s.find(flag) != -1:
            return True
    return None
    
    
def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    return next(filter(pred, iterable), default)


def func_name():
    """
    :return: name of caller
    """
    return sys._getframe(2).f_code.co_name
    
    

def filterWodsProblems(s, log, context=None):
    """
    Filter word. If not correct retirn None
    
    in:  string
    out: string
    """
    
    if context is None:
        context = func_name()
    
    # skip None
    if s is None:
        #log.warn("is None: [SKIP]")
        return None
        
    # skip single symbols
    if len(s) == 1:
        log.warn("    filter: %s: %s: len() == 1: [SKIP]", context, s)
        return None
        
    # skip words contains more than 3 symbol of two dots (ABBR?)
    #if s.count('.') > 3:
    #    log.warn("    filter: %s: %s: count('.') > 3: [SKIP]", context, s)
    #    return None

    # skip words contains :
    if s.find(':') != -1:
        log.warn("    filter: %s: %s: find(':'): [SKIP]", context, s)
        return None

    # skip more than 3 spaces
    if s.count(' ') > 3:
        log.warn("    filter: %s: %s: count(' ') > 3: [SKIP]", context, s)
        return None

    # skip #
    if s.find('#') != -1:
        log.warn("    filter: %s: %s: find('#'): [SKIP]", context, s)
        return None
    
    return s


def clean_surrogates(s):
    return str(s.encode('utf-16', 'surrogatepass').decode('utf-16'))


def pprint(*args, **kwarg):
    from pprint import PrettyPrinter
    return PrettyPrinter(indent=4).pprint(*args, **kwarg)
