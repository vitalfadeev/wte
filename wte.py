#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Wikitionary text Parser

It parse the text in Wikitionary format, like a: 
    {{also|Chat|chất|chắt|chặt|chật}}
    ==English==
    {{wikipedia}}

    ===Pronunciation===
    * {{IPA|/tʃæt/|lang=en}}
    * {{audio|en-us-chat.ogg|Audio (US)|lang=en}}
    * {{audio|EN-AU ck1 chat.ogg|Audio (AU)|lang=en}}
    * {{rhymes|æt|lang=en}}

    ===Etymology 1===
    Abbreviation of {{m|en|chatter}}. The bird sense refers to the sound of its call.

    ====Verb====
    {{en-verb|chatt}}
    [[image:Wikimania 2009 - Chatting (3).jpg|thumb|Two people '''chatting'''. (1) (2)]]

    # To be [[engage]]d in informal [[conversation]].
    #: {{ux|en|She '''chatted''' with her friend in the cafe.}}
    #: {{ux|en|I like to '''chat''' over a coffee with a friend.}}

"""

# 1) Wiktionary Loader from dump : download the file source with HTTP (This module have one parameter : Language code)
# 2) Load into memory (TreeMap): parse the source file 
# 3) Export to 9 text file JSON UTF-8
# 4) Load from JSON text file into TreeMap
# 5) Save to disk (Pickle)
# 6) Load from disk (Pickl

# Requirements:
#   pip install blist
#   pip install requests
#
# Description:
#   blist            - The blist is a drop-in replacement for the Python list the provides better performance when modifying large lists.

# Files:
# https://dumps.wikimedia.org/enwiktionary/latest/
# https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles.xml.bz2


import os
import bz2
import json
import xml.parsers.expat
import re
import pickle
import logging
 
#import wikitextparser as wtp
from blist import sorteddict
import templates
import wikoo


TXT_FOLDER   = "txt"        # folder where stored text files for debugging
CACHE_FOLDER = "cached"     # folder where stored downloadad dumps
LOGS_FOLDER  = "logs"       # log folder

# logging
log_level = logging.INFO    # log level: logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR
WORD_JUST = 24              # align size

def setup_logger(logger_name, level=logging.INFO, msgformat='%(message)s'):
    l = logging.getLogger(logger_name)

    logging.addLevelName(logging.DEBUG, "DBG")
    logging.addLevelName(logging.INFO, "NFO")
    logging.addLevelName(logging.WARNING, "WRN")
    logging.addLevelName(logging.ERROR, "ERR")

    logfile = logging.FileHandler(os.path.join(LOGS_FOLDER, logger_name+".log"), mode='w', encoding="UTF-8")
    formatter = logging.Formatter(msgformat)
    logfile.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(logfile)
    
    return l

# Exception for terminate parsing on limit
class IterStopException(Exception):
    None


class WORD_TYPES:
    NOUN = "noun" # also ===Proper noun=== {{en-proper noun}}
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    DETERMINER = "determiner"
    EXCLAMATION = "exclamation"  
    INTERJECTION = "interjection"  
    NUMERAL = "num"
    PARTICLE = "part"
    POSTPOSITION = "postp"
    
    def detect_type(self, s):
        for a in dir(self):
            if a.isupper():
                if getattr(self, a) == s.lower():
                    return getattr(self, a)
                    
        return None # not found type
        
    def get_names(self):
        """
        out:
            [
                (noun, noun),
                (Proper noun, noun),
                (section_title_lowercase, type),
            ]
        """
        names = []
        
        for a in dir(self):
            if a.isupper():
                names.append( ( getattr(self, a), getattr(self, a) ) )
                
        # fixes
        names.append( ( "Proper noun", self.NOUN ) )
            
        return names
        

class Word:
    """
    Main word class.
    Here stored info about word.
    """
    def __init__(self):
        self.LabelName = ""             #
        self.LanguageCode = ""          # (EN,FR,…)
        self.Type = ""                  #  = noun,verb… see = WORD_TYPES
        self.TypeLabelName = ""         # chatt for verb of chat
        self.ExplainationExample = [ ]  # (explaination1||Example1) (A wheeled vehicle that moves independently||She drove her car to the mall..)
        self.IsMaleVariant = None
        self.IsFemaleVariant = None
        self.MaleVariant = None         # ""
        self.FemaleVariant = None       # ""
        self.IsSingleVariant = None
        self.IsPluralVariant = None
        self.SingleVariant = None       # ""
        self.PluralVariant = None       # ""
        self.AlternativeFormsOther = [] # (British variant, usa variant, etc…)
        self.RelatedTerms = None        # [] (list of all Related terms and Derived terms)
        self.IsVerbPast = None
        self.IsVerbPresent = None
        self.IsVerbFutur = None
        self.Conjugation = None         # [ ] (All verb Conjugation (example = like, liking, liked)
        self.Synonyms = None            # [ ]
        self.Translation_EN = None      # [ ]
        self.Translation_FR = None      # [ ]
        self.Translation_DE = None      # [ ]
        self.Translation_ES = None      # [ ]
        self.Translation_RU = None      # [ ]
        self.Translation_CN = None      # [ ]
        self.Translation_PT = None      # [ ]
        self.Translation_JA = None      # [ ]

    def save_to_json(self, filename):
        save_to_json(self, filename)

    def save_to_pickle(self, filename):
        save_to_pickle(self, filename)

    def add_translation(self, lang, translation):
        # validate
        if not translation:
            # skip blank
            # skip empty
            # skip None
            return 
            
        # prepare
        storages = {
            "en": "Translation_EN",
            "de": "Translation_DE",
            "fr": "Translation_FR",
            "es": "Translation_ES",
            "ru": "Translation_RU",
            "cn": "Translation_CN",
            "pt": "Translation_PT",
            "ja": "Translation_JA"
        }

        # check lang
        if lang not in storages:
            # not supported language
            log.warning("unsupported language: " + str(lang))
            return

        # storage
        storage_name = storages.get(lang, None)
        
        # init storage
        storage = getattr(self, storage_name)
        if storage is None:
            # init
            storage = []
            setattr(self, storage_name, storage)
            
        # append
        if isinstance(translation, str):
            # one
            storage.append(translation)
            
        elif isinstance(translation, (list, tuple)):
            # [list] | (tuple)
            storage += translation
            
        else:
            log.error("unsupported type: %s", type(translation))
            #assert 0, "unsupported type"

    def __repr__(self):
        return "Word("+self.LabelName+")"


class WordsEncoder(json.JSONEncoder):
    """
    This class using in JSON encoder.
    Take object with Word objects and return dict.
    """
    def default(self, obj):
        if isinstance(obj, Word):
            # Word
            return {k:v for k,v in obj.__dict__.items() if k[0] != "_"}

        elif isinstance(obj, TreeMap):
            # TreeMap
            return {k:v for k,v in obj.store.items()}

        elif isinstance(obj, sorteddict):
            # sorteddict
            return dict(obj.items())

        # default
        return json.JSONEncoder.default(self, obj)


class TreeMap:
    def __init__(self):
        self.store = sorteddict()
        
    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key
        
    def get(self, key, defaultvalue):
        return self.store.get(key, defaultvalue)
        
    def save_to_json(self, json_filename):
        save_to_json(self.store, json_filename)

    def save_to_pickle(self, pickle_filename):
        save_to_pickle(self.store, pickle_filename)

    def load_from_json(self, json_filename):
        self.store = load_from_json(json_filename)

    def load_from_pickle(self, pickle_filename):
        self.store = load_from_pickle(pickle_filename)


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
    if filename == "con":
        filename = "reserved_con"
        
    elif filename == "aux":
        filename = "reserved_aux"
        
    return filename

def unique(lst):    
    return list(set(lst))

def get_contents(filename):
    """
    Read the file 'filename' and return content.
    """
    with open(filename, encoding="UTF-8") as f:
        return f.read()
        
    return None

def put_contents(filename, content):
    """
    Save 'content' to the file 'filename'. UTF-8.
    """
    with open(filename, "w", encoding="UTF-8") as f:
        f.write(content)

def save_text(label, text, ext=".txt"):
    """
    Save string 'text' into the file TXT_FOLDER/<label>.txt
    """
    put_contents(os.path.join(TXT_FOLDER, sanitize_filename(label) + ext), text)
    
def save_to_json(treemap, filename):
    """
    Save 'treemap' in the file 'filename'. In JSON format. Encoding UTF-8.
    """
    #folder = os.path.dirname(os.path.abspath(filename))
    #create_storage(folder)
    
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(treemap, f, cls=WordsEncoder, sort_keys=False, indent=4, ensure_ascii=False)

def load_from_json(filename):    
    """
    Load data from JSON-file 'filename'. Decode to class Word. Encoding UTF-8. 
    
    In:
        filename
    Out:
        sorteddict | None
    """
    def decode_json_object(obj):
        """
        json object decoder callback.
        """
        if "LabelName" in obj:
            word = Word()
            
            for k,v in obj.items():
                setattr(word, k, v)
            
            return word
            
        else:
            return sorteddict(obj)        

    # decode
    with open(filename, "r", encoding="UTF-8") as f:
        treemap = json.load(f, object_hook=decode_json_object)
        return treemap
        
    return None

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

def is_english(s):
    """
    Check word for all chars is English.
    
    In:
        s - string
    Out:
        True | False
    """
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


class Wikitionary:
    """
    This is the main class.
        # 1) Wiktionary Loader from dump : download the file source with HTTP (This module have one parameter : Language code)
        # 2) Load into memory (TreeMap): parse the source file 
        # 3) Export to 9 text file JSON UTF-8
        # 4) Load from JSON text file into TreeMap
        # 5) Save to disk (Pickle)
        # 6) Load from disk (Pickle)
    """
    def __init__(self):
        self.treemap = TreeMap()
        
    def download(self, lang="en", use_cached=True):
        """
        Download file from HTTPS.
        
        In:
            lang       - Language code string, like a: en, de, fr
            use_cached - True if need use cached_file. False for force run downloading.
        Out:
            local_file - local cached file name
        """
        remote_file = "https://dumps.wikimedia.org/"+lang+"wiktionary/latest/"+lang+"wiktionary-latest-pages-articles.xml.bz2"
        
        create_storage(CACHE_FOLDER)
        local_file = os.path.join(CACHE_FOLDER, lang+"wiktionary-latest-pages-articles.xml.bz2")

        # check cache
        if use_cached and os.path.exists(local_file):
            return local_file

        # download
        import requests
        import shutil
                
        r = requests.get(remote_file, auth=('usrname', 'password'), verify=False,stream=True)
        r.raw.decode_content = True
        
        log.info("Downloading....")
        with open(local_file, 'wb') as f:
            shutil.copyfileobj(r.raw, f)  
        log.info("Downloaded....[ OK ]")
        
        return local_file
    
    def parse_dump(self, dump_file, limit=None, is_save_txt=False, is_save_json=False):
        """
        Parse 'dump_file'.
        Here:
        - unzip bz2 file
        - parse xml
        - extract <page>
        - extract <label>, <text>
        - parse text
        - create Word
        - fill Word with data
        
        Extracted words saved in sorteddict self.treemap.
        Can limit of words extraction by call set_limit(N), Like a set_limit(100).
        
        In:
            dump_file - string contans local file name, like a "./ru/ruwiktionary-latest-pages-articles.xml.bz2"
        Out:
            treemap - sorteddict with words, like a: {'chat': [Word, Word, Word]}
        """
        # dump_file = "./ru/ruwiktionary-latest-pages-articles.xml.bz2"
        self.count = 0
        self.treemap = TreeMap()
        self.is_save_txt = is_save_txt
        self.is_save_json = is_save_json
        
        def callback(label, text):
            # keep english words only
            if not is_english(label):
                log_non_english.warning("%s: non english chars ... [SKIP]", label.ljust(WORD_JUST))
                return
            
            # save txt
            if self.is_save_txt:
                put_contents(os.path.join(TXT_FOLDER, sanitize_filename(label) + ".txt"), text)
            
            # main step
            words = parse_text(label, text)
            
            if words:
                storage = self.treemap.get(label, None)
                if storage is None:
                    storage = []
                    self.treemap[label] = storage
                storage += words
                
            else:
                log_no_words.warning("%s: no words ... [SKIP]", label.ljust(WORD_JUST))

            # json
            if is_save_json:
                save_to_json(words, os.path.join(TXT_FOLDER, sanitize_filename(label)+".json"))
            
            # counter
            self.count += 1
            
            if self.count % 100 == 0:
                log.info("%d", self.count)

            # limit
            if limit and (self.count >= limit):
                log.warning("Limit reached: %d ... [EXIT]", self.count)
                raise IterStopException()

        try: read_dump(dump_file, callback)
        except IterStopException: return self.treemap
        
        return self.treemap


def read_dump(dump_file, text_callback):
    """
    Read .bz2 file 'dump_file', parse xml, call 'text_callback' on each <page> tag.
    Callback format: text_callback(label, text)
    """
    stream = bz2.BZ2File(dump_file, "r")
    parser = XMLParser()
    parser.parse(stream, text_callback)
    stream.close()


class XMLParser:
    """
    XML parser. Parser xml stream, find <page>, extract all subtags and data, and run callback.
    """
    def __init__(self):
        self.inpage = False
        self.intitle = False
        self.intext = False
        self.title = ""
        self.text = ""
     
        ### BEGIN ###
        # Initializing xml parser
        self.parser = xml.parsers.expat.ParserCreate()
        
        self.parser.StartElementHandler = self.start_tag
        self.parser.EndElementHandler = self.end_tag
        self.parser.CharacterDataHandler = self.data_handler
        self.parser.buffer_text = True
        self.parser.buffer_size = 1024

    def start_tag(self, tag, attrs):
        """
        Event on open tag, like the "<page>"
        """
        if not self.inpage:
            if tag == "page":
                # flags
                self.inpage = True
                self.intitle = False
                self.intext = False
                # storages
                self.text = ""
                self.title = ""
                
        elif self.inpage:
            if tag == "title":
                self.intitle = True
                self.title = ""
                
            elif tag == "text":
                self.intext = True
                self.text = ""
                
    def data_handler(self, data):
        """
        Event on tag data, like the "<page> data here </page>"
        """
        if self.inpage:
            if self.intitle:
                # title
                self.title += data # cumulative, because can be multiple data sections
                
            elif self.intext:
                # text
                self.text += data # cumulative, because can be multiple data sections

    def end_tag(self, tag):
        """
        Event on close tag, like the "</page>"
        """
        if self.inpage:
            if tag == "page":
                self.page_callback(self.title, self.text)
                self.inpage = False

            elif tag == "title":
                self.intitle = False
                
            elif tag == "text":
                self.intext = False

    def parse(self, file_stream, page_callback):
        """
        Parse xml stream 'file_stream', and run callback 'page_callback'
        
        In:
            file_stream   - stream like a: File
            page_callback - function like a: page_callback(label, text)
            
        """
        self.page_callback = page_callback

        log.info("Processing...")
        self.parser.ParseFile(file_stream)
        log.info("Done processing.")


def oneof(*args):
    """
    Take generators and return first not None.
    
    in:  gen1, gen2
    out: gen1

    in:  None, gen2
    out: gen2
    """
    it_was = False
    
    for gen in args:
        if gen:
            for a in gen:
                it_was = True
                yield a
                
            if it_was:
                break

def cleanup(s):
    """
    Cleanup strin 's'.
    It used for cleanup explanations.
    
    in:  "The text with [[name]]. {{templates}}"
    out: "The text with name."
    """
    # remove brackets like a [[...]]
    # remove templates
    
    # remove ###
    i = 0
    l = len(s)
    if l > 0 and s[0] in "#*":
        while i < l and s[i] in "#*: ":
            i += 1
        
        s = s[i:]
        
    # extract from brackets, like a [[ text ]]
    s = s.replace("[[", "").replace("]]", "")

    # extract from brackets, like a ''' text '''
    s = s.replace("'''", "")

    # extract from brackets, like a '' text ''
    s = s.replace("''", "'")

    # remove head and tail spaces
    s = s.strip()

    return s


def get_explainations(section, label):
    """
    Find explainations in section 'section'
    
    out: [...]
    """
    explainations = []
    
    for li in section.find_lists():
        #print(li.data)
        #print(li, li.is_empty(), li.has_templates_only())
        # ... scan list
        if li.has_templates_only():
            # check subtemplate
            for sub in li.find_lists():
                if sub.has_templates_only():
                    continue
                else:
                    # OK. add
                    explainations.append(sub.get_text())
        else:
            if li.base.endswith(":"):
                # skip example
                pass
            else:
                # OK. add
                explainations.append(li.get_text())
        
    return explainations
    
def get_alternatives(section):
    """
    Find alternatives in section 'section'
    
    out: {en:[..], de:[...]}
    """
    # ==English== section here
    # ===Alternative forms===
    # * {{l|en|hower}} {{qualifier|obsolete}}
    
    result = []
    
    for sec in section.find_section_recursive("Alternative forms"):
        for t in sec.find_templates_recursive():
            # * {{l|en|hower}}
            if t.name == "l":
                lang = t.arg(0)
                term = t.arg(1)
                
                if term:
                    result.append( (lang, term) )

    #
    bylang = {}
    
    #
    for lang, term in result:
        if lang in bylang:
            bylang[lang].append(term)
        else:
            bylang[lang] = []
            bylang[lang].append(term)

    return bylang

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
    
    
    #s = "{{rel-top|related terms}}"
    #lst = self.get_list_after_string(parsed, s)
    
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
    
    for obj in section.find_objects_between_templates_recursive("rel-top", "rel-bottom", "related terms"):
        if isinstance(obj, wikoo.LI):
            for t in obj.find_templates():
                if t.name == "l":
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )

    # case 2
    # {{rel-top|related terms}}
    for sec in section.find_section_recursive("Related terms"):
        for t in sec.find_templates_recursive():
            # * {{l|en|hower}}
            if t.name == "l":
                lang = t.arg(0)
                term = t.arg(1)
                
                if term:
                    result.append( (lang, term) )

    # case 3
    # {{en-simple past of|do}}
    for t in section.find_templates_recursive():
        # * {{l|en|hower}}
        if t.name == "en-simple past of":
            lang = t.arg("lang")
            term = t.arg(0)
            
            if term:
                result.append( (lang, term) )
    
        elif t.name == "present participle of":
            # {{present participle of|do}}
            lang = t.arg("lang")
            term = t.arg(0)
            
            if term:
                result.append( (lang, term) )
    
        elif t.name == "en-third-person singular of":
            # {{en-third-person singular of|do}}
            lang = t.arg("lang")
            term = t.arg(0)
            
            if term:
                result.append( (lang, term) )
    
        elif t.name == "inflection of":
            # {{inflection of|do||past|part|lang=en}}
            lang = t.arg("lang")
            term = t.arg(0)
            
            if term:
                result.append( (lang, term) )
    

    # case 4
    # get from parents
    for t in section.find_templates_in_parents():
        if t.name == "m":
            # {{m|en|doe|t=female deer}}
            lang = t.arg(0)
            term = t.arg(1)
            
            if term:
                result.append( (lang, term) )
    
                    
    #
    bylang = {}
    
    #
    for lang, term in result:
        if lang in bylang:
            bylang[lang].append(term)
        else:
            bylang[lang] = []
            bylang[lang].append(term)

    return bylang
    
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
    for obj in section.find_objects_between_templates_recursive("trans-top", "trans-bottom"):    
        if isinstance(obj, wikoo.LI):
            for t in obj.find_templates():
                # {{t-simple|za|max|langname=Zhuang}}
                if t.name.lower() == "t-simple":
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )
                            
                elif t.name.lower() == "t+":
                    # {{t+|zu|ihhashi|c5|c6}}
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )
                            
                elif t.name.lower() == "t":
                    # {{t|ude|муи }}
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )

    # case 2
    # * {{t|en|cat}} 
    for t in section.find_templates_in_parents():
                # {{t-simple|za|max|langname=Zhuang}}
                if t.name.lower() == "t-simple":
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )
                            
                elif t.name.lower() == "t+":
                    # {{t+|zu|ihhashi|c5|c6}}
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )
                            
                elif t.name.lower() == "t":
                    # {{t|ude|муи }}
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )    

    #
    bylang = {}
    
    #
    for lang, term in result:
        if lang in bylang:
            bylang[lang].append(term)
        else:
            bylang[lang] = []
            bylang[lang].append(term)

    return bylang

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

    ====Synonyms====
    * {{sense|period of sixty minutes|a season or moment}} {{l|en|stound}} {{qualifier|obsolete}}
    """
    
    result = []
    
    # here is section like a ====Noun==== or ====Verb====
    # find section =====Synonyms=====
    for sec in section.find_section_recursive("Synonyms"):
        for t in sec.find_templates_recursive():
            # find {{sense|animal}} | {{l|en|horsie}}
            # remove brackets like a [[...]]
            # remove templates
            # get example
            if 0 and t.name == "sense": # disabled, because words only
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )
                
            elif t.name == "l":
                    lang = t.arg(0)
                    term = t.arg(1)
                    
                    if term:
                        result.append( (lang, term) )
    
    #
    bylang = {}
    
    #
    for lang, term in result:
        if lang in bylang:
            bylang[lang].append(term)
        else:
            bylang[lang] = []
            bylang[lang].append(term)

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
    for t in section.find_templates_recursive():
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
    for t in section.find_templates_recursive():
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label)
            
            if gender == "m":
                return True
                
    return None

def is_female_variant(section, label):
    # From {{inh|en|enm|cat}}, {{m|enm|catte}}, 
    # from {{inh|en|ang|catt||male cat}}, {{m|ang|catte||female cat}}, 
    # from {{inh|en|gem-pro|*kattuz}}.
    for t in section.find_templates_recursive():
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label)
            
            if gender == "f":
                return True
                
    return None

def is_singular(section, label):
    # case 1
    for t in section.find_templates_recursive():
        if t.name == "en-third-person singular of":
            (s, p, is_uncountable) = templates.en_noun(t, label)
            
            if p:
                return True
                
        elif t.name == "en-noun": 
        # case 2
            (s, p, is_uncountable) = templates.en_noun(t, label)
            
            if p:
                return True
                
        elif t.name == "head": 
            lang = t.arg(0)
            flag = t.arg(0)
            if flag == "noun plural form":
                return True


    return None

def is_plural(section):
    # {{plural of|cat|lang=en}}
    for t in section.find_templates_recursive():
        if t.name == "plural of":
            #(lang, single, showntext) = templates.plural_of(t, label)            
            return True
    
    return None
    
def is_verb_present(section, label):
    # {{present participle of}}
    for t in section.find_templates_recursive():
        if t.name == "present participle of":
            # {{present participle of|do|lang=en|nocat=1}}
            return True
            
        elif t.name == "en-third-person singular of":
            return True
            
    return None

def is_verb_past(section, label):
    # {{en-past of}}
    for t in section.find_templates_recursive():
        if t.name == "en-past of":
            return True
            
        elif t.name == "en-simple past of":
            return True
            
        elif t.name == "inflection of":
            # {{inflection of|do||past|part|lang=en}}
            a2 = t.arg(2)
            if a2 == "past":
                return True
            
    return None

def is_verb_futur(section, label):
    return None

def get_singular_variant(section, label):
    return None

def get_plural_variant(section, label):
    for t in section.find_templates_recursive():
        if t.name == "ang-noun":
            (head, gender, plural, plural2) = templates.ang_noun(t, label)
            
            if plural is not None:
                return plural

        elif t.name == "en-noun":
            (single, plural, is_uncountable) = templates.en_noun(t, label)

            if plural:
                return plural
                
    return None

def get_words(label, text):
    """
    Main parser tool.
    
    in:  label, text
    out: [Word, Word, Word]
    """
    # get section ==English==
    # if not: get root
    # for each section Noun | Verb | ...
    #   get list. first list only
    #     get explainations
    #
    words = []
    
    root = wikoo.parse(text)
    #wikoo.dump_section(root, show_sections_only=True)
    #exit(0)
    
    supported_types = WORD_TYPES().get_names() 
    supported_titles = [title for (title, type_code) in supported_types]
    is_english_found = False
    
    #    
    for english_section in root.find_section_recursive("English"):
        is_english_found = True
    
        # common alternatives
        alternatives = get_alternatives(english_section).get("en", None)

        # common translations
        #translations = get_translations(english_section, label)

        # by types
        is_type_found = False
        
        for section in english_section.find_sections_recursive( supported_titles ):
            is_type_found = True
            
            #print(english_section, section)
            # word
            word = Word()
            words.append(word)
            
            # label
            word.LabelName = label
            
            # lang
            word.LanguageCode = "en"
            
            # type
            word.Type = WORD_TYPES().detect_type(section.title)
            word.TypeLabelName = section.title
            
            # explainations
            word.ExplainationExample = [
                    {"cln":cleanup(expl), "raw":expl} for expl in get_explainations(section, label)
                ]
        
            # alternatives
            # type alternatives
            #type_alternatives = get_alternatives(section)
            word.AlternativeFormsOther = alternatives

            # relates
            related = get_related(section, label)
            word.RelatedTerms = related.get("en", related.get(None, None))
            
            # translations
            type_translations = get_translations(section, label)
            if type_translations:
                translations = type_translations
                word.add_translation("en", translations.get("en", None))
                word.add_translation("en", translations.get(None, None))
                word.add_translation("fr", translations.get("fr", None))
                word.add_translation("de", translations.get("de", None))
                word.add_translation("es", translations.get("es", None))
                word.add_translation("ru", translations.get("ru", None))
                word.add_translation("cn", translations.get("cn", None))
                word.add_translation("pt", translations.get("pt", None))
                word.add_translation("ja", translations.get("ja", None))
            else:
                log.warning("%s: translations not found: for %s", label.ljust(WORD_JUST), section.title)
            
            # translations
            word.Synonyms = get_synonyms(section, label).get("en", None)
            
            # conjugations
            word.Conjugation = get_conjugations(section, label)
            
            # male | female
            if is_male_variant(section, label):
                word.IsMaleVariant = True

            if is_female_variant(section, label):
                word.IsFemaleVariant = True

            # singular | plural
            if is_singular(section, label):
                word.IsSingleVariant = True
            
            # single variant
            single = get_singular_variant(section, label)
            
            if single is not None:
                word.SingleVariant = single
            
            # plural variant
            plural = get_plural_variant(section, label)
            
            if plural is not None:
                word.PluralVariant = plural
                
            # verb
            word.IsVerbPresent  = is_verb_present(section, label)
            word.IsVerbPast     = is_verb_past(section, label)
            word.IsVerbFutur    = is_verb_futur(section, label)
            
        if not is_type_found:
            log_non_english.warning("%s: type section not found... [SKIP]", label.ljust(WORD_JUST))

    if not is_english_found:
        log_non_english.warning("%s: English section not found... [SKIP]", label.ljust(WORD_JUST))
     
    return words


def parse_text(label, text):
    root = wikoo.parse(text)
    words = get_words(label, text)
    return words


def one_file(label = "cat"):
    """
    Parse only on word 'label'. (For Debugging)
    
    Get text from the test/<label>.txt
    Save to the test/<label>.json
    """
    log.info("Word: %s", label)
    src_file = "./test/" + label + ".txt"
    log.info("Loading from: %s", src_file)
    text = get_contents(src_file)

    # parse
    log.info("Parsing")
    words = parse_text(label, text)
    
    # pack
    treemap = TreeMap()
    treemap[label] = words
    
    # save to json
    json_file = os.path.join(TXT_FOLDER, sanitize_filename(label) + ".json")
    log.info("Saving to: %s", json_file)
    save_to_json(treemap, json_file)

    log.info("Status: words:%d, labels:%s", len(words), str([w.LabelName for w in words]))
    log.info("Done!")
        

# setup loggers
create_storage(LOGS_FOLDER)
create_storage(TXT_FOLDER)
logging.basicConfig(level=log_level)
log             = setup_logger('main', msgformat='%(levelname)s: %(message)s')
log_non_english = setup_logger('log_non_english')
log_unsupported = setup_logger('log_unsupported')
log_no_words    = setup_logger('log_no_words')
