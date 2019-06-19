#!/bin/env python3

import os
import bz2
import json
import xml.parsers.expat
import importlib
from collections.abc import Iterable

from blist import sorteddict
from helpers import create_storage, put_contents, get_contents, sanitize_filename
from helpers import load_from_pickle, save_to_pickle, convert_to_alnum, proper, deduplicate
from helpers import remove_comments, extract_from_link
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found
from helpers import is_ascii
import helpers
import wikoo
from wikoo import Section, Template, Link, Li, Dl, Dt, Dd, Header, Mined
from miners import find_explainations
from wiktionary import WikictionaryItem


TXT_FOLDER      = "txt"     # folder where stored text files for debugging
CACHE_FOLDER    = "cached"  # folder where stored downloadad dumps
WORD_JUST       = 24        # align size
create_storage(TXT_FOLDER)


class KEYS:
    """ Data keys for using in data mining """
    IS_TYPE_SECTION = "IS_TYPE_SECTION"
    LANG        = "lang"
    TYPE        = "type"
    INHERITED   = "inherited"
    TRANSLATION = "translation"
    SYNONYM     = "synonym"
    LABEL       = "label"
    ALTER       = "alter"
    RELATED     = "related"
    EXPLAIN     = "explain"
    PAST        = "past"
    PRESENT     = "present"
    PLURAL      = "plural"
    SINGULAR    = "singular"
    MALE        = "male"
    FEMALE      = "female"


class WORD_TYPES:
    """ Word type of speech"""
    ROOT        = "root"  # also ===Proper noun=== {{en-proper noun}}
    NOUN        = "noun"  # also ===Proper noun=== {{en-proper noun}}
    VERB        = "verb"
    PROVERB     = "proverb"
    CONVERB     = "converb"
    ADJECTIVE   = "adjective"
    ADVERB      = "adverb"
    ADNOUN      = "adj_noun"
    PRONOUN     = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    DETERMINER  = "determiner"
    EXCLAMATION = "exclamation"
    INTERJECTION= "interjection"
    NUMERAL     = "num"
    PARTICLE    = "part"
    PARTICIPLE  = "participle"
    POSTPOSITION= "postp"
    CHARACTER   = "character"
    DIGIT       = "digit"
    ABBREV      = "abbrev"
    AFFIX       = "affix"
    INFIX       = "infix"
    NAME        = "name"
    PREFIX      = "prefix"
    INTERFIX    = "interfix"
    SUFFIX      = "suffix"
    SYMBOL      = "symbol"
    PUNCT       = "punct"
    NUMBER      = "number"
    PHRASE      = "phrase"
    ARTICLE     = "article"
    COUNTER     = "counter"
    CLITIC      = "clitic"
    CIRCUMFIX   = "circumfix"
    CIRCUMPOS   = "circumpos"
    CLASSIFIER  = "classifier"
    PREDICATIVE = "predicative"
    POSTP       = "postp"
    ORDINAL     = "ordinal"
    CLAUSE      = "clause"
    LETTER      = "letter"
    GERUND      = "gerund"
    CMD         = "cmd"
    COMBINING_FORM = "combining_form"
    ADJ_COMP    = "adj_comp"
    INTRO       = "intro"

    def detect_type(self, s):
        for a in dir(self):
            if a.isupper():
                if getattr(self, a) == s.lower():
                    return getattr(self, a)

        return None  # not found type


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
                names.append((getattr(self, a), getattr(self, a)))

        # fixes
        names.append(("Proper noun", self.NOUN))

        return names


class WordsEncoder(json.JSONEncoder):
    """
    This class using in JSON encoder.
    Take object with Word objects and return dict.
    """

    def default(self, obj):
        if isinstance(obj, WikictionaryItem):
            # Word
            return {k: v for k, v in obj.__dict__.items() if k[0] != "_"}

        elif isinstance(obj, TreeMap):
            # TreeMap
            return {k: v for k, v in obj.store.items()}

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

    def items(self):
        return self.store.items()

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

    def add_words(self, label, words):
        """
        Add words 'words' to the store.
        :param label: label
        :param words: words list
        """
        if words:
            storage = self.store.get(label, None)

            if storage is None:
                if len(words) == 1:
                    self.store[label] = words[0]
                else:
                    self.store[label] = words

            elif isinstance(storage, WikictionaryItem):
                if len(words) == 1:
                    stored_word = storage
                    self.store[label] = [stored_word] + words

            elif isinstance(storage, list):
                storage += words

            else:
                assert 0, "unsupported"


# Exception for terminate parsing on limit
class IterStopException(Exception):
    None


def save_text(label, text, ext=".txt"):
    """
    Save string 'text' into the file TXT_FOLDER/<label>.txt
    """
    put_contents(os.path.join(TXT_FOLDER, sanitize_filename(label) + ext), text)


def save_to_json(treemap, filename):
    """
    Save 'treemap' in the file 'filename'. In JSON format. Encoding UTF-8.
    """
    # folder = os.path.dirname(os.path.abspath(filename))
    # create_storage(folder)

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
            word = WikictionaryItem()

            for k, v in obj.items():
                setattr(word, k, v)

            return word

        else:
            return sorteddict(obj)

            # decode

    with open(filename, "r", encoding="UTF-8") as f:
        treemap = json.load(f, object_hook=decode_json_object)
        return treemap

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


def download(lang="en", use_cached=True):
    """
    Download file from HTTPS.

    In:
        lang       - Language code string, like a: en, de, fr
        use_cached - True if need use cached_file. False for force run downloading.
    Out:
        local_file - local cached file name
    """
    remote_file = "https://dumps.wikimedia.org/" + lang + "wiktionary/latest/" + lang + "wiktionary-latest-pages-articles.xml.bz2"

    create_storage(CACHE_FOLDER)
    local_file = os.path.join(CACHE_FOLDER, lang + "wiktionary-latest-pages-articles.xml.bz2")

    # check cache
    if use_cached and os.path.exists(local_file):
        return local_file

    # download
    import requests
    import shutil

    r = requests.get(remote_file, auth=('usrname', 'password'), verify=False, stream=True)
    r.raw.decode_content = True

    log.info("Downloading....")
    with open(local_file, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    log.info("Downloaded....[ OK ]")

    return local_file


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
        self._parser = xml.parsers.expat.ParserCreate()

        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.cdata
        self._parser.buffer_text = True
        self._parser.buffer_size = 1024

    def start(self, tag, attrs):
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

    def cdata(self, data):
        """
        Event on tag data, like the "<page> data here </page>"
        """
        if self.inpage:
            if self.intitle:
                # title
                self.title += data  # cumulative, because can be multiple data sections

            elif self.intext:
                # text
                self.text += data  # cumulative, because can be multiple data sections

    def end(self, tag):
        """
        Event on close tag, like the "</page>"
        """
        if self.inpage:
            if tag == "page":
                self.page_callback(self.lang, self.title, self.text, self.limit, self.is_save_txt, self.is_save_json, self.is_save_xml, self.is_save_templates)
                self.inpage = False

            elif tag == "title":
                self.intitle = False

            elif tag == "text":
                self.intext = False

    def parse(self, file_stream, page_callback, lang="en", limit=10, is_save_txt=False, is_save_json=False, is_save_xml=False, is_save_templates=False):
        """
        Parse xml stream 'file_stream', and run callback 'page_callback'

        In:
            file_stream   - stream like a: File
            page_callback - function like a: page_callback(label, text)

        """
        self.page_callback = page_callback
        self.lang = lang
        self.limit = limit
        self.is_save_txt = is_save_txt
        self.is_save_json = is_save_json
        self.is_save_xml = is_save_xml
        self.is_save_templates = is_save_templates

        log.info("Processing...")
        self._parser.ParseFile(file_stream)
        log.info("Done processing.")


# 
# STRUCT = [
#   LANG_SECTION, [
#     TOS_SECTION, [
#       EXPLAINATION, # <- Li, Dl
#       EXPLAINATION
#     ],
#     TOS_SECTION, [
#       EXPLAINATION
#     ],
#   ],
#   LANG_SECTION, []
# ]
#
# word, LANG, TOS, EXPL
# word, LANG, TOS, EXPL
# word, LANG, TOS, EXPL


def build_struct(lm, label, tree):
    """
    Used in word article scanner.

    in:
        lm      Language module
        label   word label
        tree    parsed article tree
    out:
        Lang
          Type-of-speech
            Explaination
    """
    # (name, childs), childs = (name, childs)
    struct = [] # [ (LANG, [ (TOS, [ (expl), ] ), ]), ]
    
    is_lang_found = False
    is_tos_found = False
    
    # Lang sections
    for ls in tree.find_top_objects(Section, lm.is_lang_section, recursive=True):
        is_lang_found = True
        tos = []
        struct.append( (ls, tos) )

        # TOS sections
        for ts in ls.find_top_objects(Section, lm.is_tos_section, recursive=True):
            is_tos_found = True
            expl = []
            tos.append( (ts, expl) )
       
            # Explainations
            for e in find_explainations(ts, lm.is_expl_section):
                expl.append( (e, []) )
                
    #
    if not is_lang_found:
        log_lang_section_not_found.warn('%s', label)
    else:
        if not is_tos_found:
            log_tos_section_not_found.warn('%s', label)
            
    return struct


def dump_struct(struct, level=0):
    # (name, childs), childs = (name, childs)
    # [ (LANG, [ (TOS, [ (expl), ] ), ]), ]
    for (name, childs) in struct:
        print("  "*level, name)
        dump_struct(childs, level+1)


def dump_tree(root, level=0, types=None, exclude=None):
    print( "  "*level, root, ":", id(root))

    for c in root.childs:
        if types and isinstance(c, types):
            if (exclude is None) or (c not in exclude):
                dump_tree(c, level+1, types, exclude)


# scan search context
def scan_struct(lm, struct, root_word, level=0):
    """
    Walk on the Lang,Type-of-speech,Explaination and mine data

    in:
        lm          Language module
        struct      struct (Lang,Type-of-speech,Explaination, see: build_struct)
        root_word   Word base template
    out:
        words       list with mined words
    """
    words = []
    
    for (search_context, childs) in struct:
        word = root_word.clone()
        words.append(word)

        excludes = [sc for (sc, c) in childs]
        
        # do extraction
        lm.Type(search_context, excludes, word)
        lm.IsMale(search_context, excludes, word)
        lm.IsFeminine(search_context, excludes, word)
        lm.IsSingle(search_context, excludes, word)
        lm.IsPlural(search_context, excludes, word)        
        lm.SingleVariant(search_context, excludes, word)
        lm.PluralVariant(search_context, excludes, word)
        lm.MaleVariant(search_context, excludes, word)
        lm.FemaleVariant(search_context, excludes, word)
        lm.IsVerbPast(search_context, excludes, word)
        lm.IsVerbPresent(search_context, excludes, word)
        lm.IsVerbFutur(search_context, excludes, word)
        lm.Conjugation(search_context, excludes, word)
        lm.Synonymy(search_context, excludes, word)
        lm.Antonymy(search_context, excludes, word)
        lm.Hypernymy(search_context, excludes, word)
        lm.Hyponymy(search_context, excludes, word)
        lm.Meronymy(search_context, excludes, word)
        lm.Holonymy(search_context, excludes, word)
        lm.Troponymy(search_context, excludes, word)
        lm.Otherwise(search_context, excludes, word)
        lm.AlternativeFormsOther(search_context, excludes, word)
        lm.RelatedTerms(search_context, excludes, word)
        lm.Coordinate(search_context, excludes, word)
        lm.Translation(search_context, excludes, word)

        # explaination caontext
        if lm.is_expl_section(search_context) or isinstance(search_context, (Li, Dl)):
            lm.LabelType(search_context, excludes, word)
            lm.ExplainationRaw(search_context, excludes, word)
            lm.ExplainationTxt(search_context, excludes, word)
            lm.ExplainationExamplesRaw(search_context, excludes, word)
            lm.ExplainationExamplesTxt(search_context, excludes, word)

        #print("  "*level, search_context, word.Type, word.IsMale)
        
        # recursive
        words += scan_struct(lm, childs, word, level+1)
        
    return words


def try_well_formed_structure(lang, label, tree):
    """ Walk on well-formed structure of article """
    lm = importlib.import_module(lang)
    
    words = []

    # struct
    # (name, childs), childs = (name, childs)
    # [ (LANG, [ (TOS, [ (expl), ] ), ]), ]
    struct = build_struct(lm, label, tree)
    #dump_struct(struct)
    #exit(2)
    
    # base word
    word = WikictionaryItem()
    word.LabelName = label
    word.LanguageCode = lang
    
    # scan for words
    words = scan_struct(lm, struct, word)
    words = list( filter(lambda w: w.Type, words) ) # with type
    words_with_explaination = list( filter(lambda w: w.LabelType is not None, words) ) # with explaination

    if words_with_explaination:
        words = words_with_explaination

    if not words:
        log_no_words.warn("%s", label)

    return words
        

def preprocess(lang, callback, limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False):
    """ Prepare data: unzip, init xml parser """
    dump_file = download(lang)
    
    with bz2.open(dump_file, "r") as xml_stream:
        parser = XMLParser()
        parser.parse(xml_stream, callback, lang=lang, limit=limit, is_save_txt=is_save_txt, is_save_json=is_save_json, is_save_templates=is_save_templates) # call process() here


def process(lang, label, text,  limit=0, is_save_txt=False, is_save_json=False, is_save_xml=False, is_save_templates=False):
    """ This function emitted on each article. Called from XML parser """
    log.info("process(%s, %s)", lang, label)
    
    # setup context
    wikoo.Context.label = label
    
    # filter
    if not label.isalnum():
        log.warn("non alnum char (%s, %s)... [SKIP]", lang, label)
        return []

#    if not is_ascii(label):
#        log.warn("non ascii char (%s, %s)... [SKIP]", lang, label)
#        return []

    # save txt
    if is_save_txt:
        put_contents(os.path.join(TXT_FOLDER, sanitize_filename(label) + ".txt"), text)
        
    # skip #REDIRECT
    if text.startswith("#REDIRECT "):
        label_to = text[len("#REDIRECT "):]
        log_no_words.warn("REDIRECT %s -> %s... [SKIP]", label, label_to)
        return []

    # process
    tree  = phase1(text)
    tree  = phase2(lang, tree)

    # debug. save tmplates and sections
    if is_save_templates:
        for s in tree.find_objects(Section, recursive=True):
            for t in s.find_objects(Template, recursive=True, exclude=list(s.find_objects(Section))):
                helpers.add_template(s, t)
        return  []

    words = phase3(lang, tree, label)
    #words = phase4(lang, mined, label)

    if not words:
        return []

    flag  = postprocess(words, label)
    
    return  words


def phase1(text):
    """ Prepare extracted text. Make object representation of article: ==English== -> Header(English), {{en-noun}} -> Template(en-noun) """
    log.debug("phase1()")
    
    # remove BOM
    if text and text.startswith('\uFEFF'):
        text = text[1:]
        
    text = "\n" + text + "\n" # fix. for detection '\n=='
    
    tree = wikoo.parse(text)
    return tree
    

def phase2(lang, tree):
    """
    Build tree

    Section(en)
      Section(Noun)
        Section(Translations)
      Section(Verb)
        Section(Translations)
    """
    log.debug("phase2()")
    lm = importlib.import_module(lang)

    #wikoo.dump(tree)
    #wikoo.dump(tree, 0, (Section, Li, Dl, wikoo.Header))
    #exit(4)

    # add headers from templates. {{-noun-}} -> Header( Noun )
    for t in tree.find_objects(Template, recursive=False):
        # add header        
        if t.name in lm.SECTION_NAME_TEMPLATES and lm.SECTION_NAME_TEMPLATES[t.name](t):
            header = Header()
            header.name = t.name
            header.level = 0 # default level
            t.parent.add_child(header, before=t)
            header.add_child(t)
            
        elif hasattr(lm, "is_lang_template") and lm.is_lang_template(t):
            header = Header()
            header.name = t.name
            header.level = 1
            t.parent.add_child(header, before=t)
            header.add_child(t)
            
        elif t.name.startswith('-') and t.name.endswith('-'): # -trad-
            header = Header()
            header.name = t.name
            header.level = 2
            t.parent.add_child(header, before=t)
            header.add_child(t)
            
    # update name for templated Headers
    for header in tree.find_objects(Header):
        for t in header.find_objects(Template):
            # name
            name_fetcher = lm.SECTION_NAME_TEMPLATES.get(t.name, None)
            
            if callable(name_fetcher):
                name = name_fetcher(t)
            elif name_fetcher is None:
                name = None
            else:
                name = name_fetcher

            if name:
                header.name = name.strip().lower()
                
                # level
                if header.level == 0 or header.name in lm.LANG_SECTIONS:
                    if header.name in lm.LANG_SECTIONS:
                        header.level = 1
                    elif header.name in lm.TOS_SECTIONS:
                        header.level = 2
                    else:
                        header.level = 4
                break # first template only

    # fix absent lang header
    for header in tree.find_objects(Header):
        # find 1st header. if TOS header
        if header.name in lm.TOS_SECTIONS:
            # add lang header above
            lang_header = Header()
            lang_header.name = lang
            lang_header.level = 1
            tree.add_child(lang_header, before=header)
        break
   
    #wikoo.dump(tree, 0, (Section, Li, Dl, wikoo.Header))
    #exit(4)

    # structure. lists. sections.
    tree = wikoo.pack_lists(tree)
    tree = wikoo.pack_sections(tree)

    return tree


def try_not_well_formed(tree):
    pass


def phase3(lang, tree, label):
    """ Mine data """
    log.debug("phase3(%s, %s)", lang, label)

    mined = tree
    #wikoo.dump(tree, 0, (Section, wikoo.Header))
    #exit(4)
    
    lm = importlib.import_module(lang)
    words = try_well_formed_structure(lang, label, tree)
    
    if 0 and len(words) == 0:
        words = try_not_well_formed(tree)

    if 0:
        # for each section
        for section in tree.find_objects(Section, recursive=True):
            section.mined = []
            
            section.mined.append( ("SECTION_NAME", section.name, "hardcoded") )

            # mine data
            for (key, data, source) in tscan(lang, section, label):
                log.debug( "mined: %s: %s: %s", key, data, source )
                section.mined.append( (key, data, source) )
        
    return words

    
def phase4(lang, mined, label):
    log.debug("phase4()")

    # word for each type: verb, noun, enverb
    # word for each explaination
    #wikoo.dump(mined, level=0, types=(Section, Li))

    # helpers
    def is_type_section(mined):
        for (key, data, source) in mined:
            if key == KEYS.IS_TYPE_SECTION and data == True:
                return True
        return None
    
    def get_lang(mined):
        for (key, data, source) in mined:
            if key == KEYS.LANG:
                return data
        return None
    
    def get_type(mined):
        for (key, data, source) in mined:
            if key == KEYS.TYPE:
                return data
        return None

    def get_is_male(mined):
        for (key, data, source) in mined:
            if key == KEYS.MALE and data == True:
                return True
        return None

    def get_is_female(mined):
        for (key, data, source) in mined:
            if key == KEYS.FEMALE and data == True:
                return True
        return None

    def get_is_singular(mined):
        for (key, data, source) in mined:
            if key == KEYS.SINGULAR and data == True:
                return True
        return None

    def get_is_plural(mined):
        for (key, data, source) in mined:
            if key == KEYS.PLURAL and data == True:
                return True
        return None

    def get_related(mined):
        result = [ data for (key, data, source) in mined if key == KEYS.ALTER ]
        return result if result else None

    def get_synonyms(mined):
        result = [ data for (key, data, source) in mined if key == KEYS.SYNONYM ]
        return result if result else None

    def get_explinations(mined):
        return [ data for (key, data, source) in mined if key == KEYS.EXPLAIN ]

    def get_translations(mined):
        return [ data for (key, data, source) in mined if key == KEYS.TRANSLATION ]

    def mine_recursive(root, word=None, section_lang=None, level=0):
        result = []
        
        for c in root.childs:
            # for sections
            if isinstance(c, Section):
                section = c
                
                # with mined
                if section.mined:
                    # find lang section
                    if section_lang is None:
                        section_lang = get_lang(section.mined)

                    if section_lang:
                        # debug
                        #for m in section.mined:
                        #    print("  "*level, m)
                            
                        if word:
                            # fill parent word
                            pass
                        else:
                            # create word
                            type = get_type( section.mined )
                            
                            if type:                    
                                # Word
                                word = WikictionaryItem()
                                word.LanguageCode = section_lang
                                word.LabelName = label
                                word.Type = type
                            else:
                                pass # SKIP (non type, non word)

                        if word:
                            # Word filling
                            # Male
                            word.IsMale = get_is_male( section.mined )

                            # Female
                            word.IsFeminine = get_is_female( section.mined )

                            # Single
                            word.IsSingle = get_is_singular( section.mined )
                            
                            # Plural
                            word.IsPlural = get_is_plural( section.mined )
                            
                            # Related
                            rela = get_related( section.mined )
                            if rela:
                                for (term_lang, term) in rela: 
                                    if term_lang is None or term_lang == lang:
                                        word.add_related(term_lang, term)

                            # Synonyms
                            syno = get_synonyms( section.mined )
                            if syno:
                                for (term_lang, term) in syno: 
                                    if term_lang is None or term_lang == lang:
                                        word.add_synonym(term_lang, term)
                            
                            # Translations
                            tran = get_translations( section.mined )
                            if tran:
                                for (term_lang, term) in tran: 
                                    if term_lang is None or term_lang == lang:
                                        word.add_translation(term_lang, term)
                                                                            
                            # Explainations
                            if is_type_section( section.mined ):
                                expl = get_explinations( section.mined )
                                if expl and len(expl) > 0:
                                    for e in expl:
                                        w = word.clone()
                                        w.ExplainationRaw = e.get_raw()
                                        w.ExplainationTxt = e.get_text()
                                        #w.ExplainationExamplesRaw = e.get_raw()
                                        #w.ExplainationExamplesTxt = e.get_text()
                                        w.LabelType = get_label_type(e)
                                        result.append(w)
                                else:
                                    result.append(word)
                
                # recursive
                result += mine_recursive(section, word, section_lang, level+1)
                
        return result

    # main func
    words = mine_recursive(mined, None, None)

    return words
    
    
def postprocess(words, label):
    """ Save to DB """
    flag = None
    if words:
        for i, word in enumerate(words):
            print_table_record(word, print_header=(i==0))

    if 1:
        if words:
            db = words[0].connect()
            for word in words:
                word.save_to_db(autocommit=False, db=db)
            db.commit()

    return flag


def print_table_record(word, print_header=False):
    """ Beauty logging tool """
    attrs = [
        "LabelName",
        "LabelType",
        "LanguageCode",
        "Type",
        "ExplainationRaw",
        "ExplainationTxt",
        #"ExplainationExamplesRaw",
        #"ExplainationExamplesTxt",
        "IsMale",
        "IsFeminine",
        "IsNeutre",
        "IsSingle",
        "IsPlural",
        "SingleVariant",
        "PluralVariant",
        "MaleVariant",
        "FemaleVariant",
        "IsVerbPast",
        "IsVerbPresent",
        "IsVerbFutur",
        "Conjugation",
        "Synonymy",
        "Antonymy",
        "Hypernymy",
        "Hyponymy",
        "Meronymy",
        "Holonymy",
        "Troponymy",
        "Otherwise",
        "AlternativeFormsOther",
        "RelatedTerms",
        "Coordinate",
        "Translation_EN",
        "Translation_FR",
        "Translation_DE",
        "Translation_IT",
        "Translation_ES",
        "Translation_RU",
        "Translation_PT",
    ]
    header = []
    if print_header:
        for a in attrs:
            s = ""
            for c in a:
                if c.isalpha() and c == c.upper():
                    s += c
                    if len(s) >= 1:
                        break
            header.append(s.rjust(2))
        log.info(" ".join(header))

    row = []
    for a in attrs:
        value = getattr(word, a)
        s = str(len(value)) if value and isinstance(value, (tuple, list)) else ('*' if value else '-')
        row.append(s.rjust(2))
    log.info(" ".join(row))


def one_file(lang, label):
    """
    Parse only on word 'label'. (For Debugging)

    Get text from the test/<label>.txt
    Save to the test/<label>.json
    """
    log.info("Word: %s", label)
    src_file = os.path.join(TXT_FOLDER, lang, label + ".txt")
    log.info("Loading from: %s", src_file)
    text = get_contents(src_file)

    # parse
    log.info("Parsing")
    words = process(lang, label, text)

    # pack
    treemap = TreeMap()
    treemap[label] = list( words )

    # save to json
    json_file = os.path.join(TXT_FOLDER, sanitize_filename(label) + ".json")
    log.info("Saving to: %s", json_file)
    save_to_json(treemap, json_file)

    log.info("Saving to DB")
    import sql
    sql.SQLWriteDB( sql.DBWikictionary, treemap )

    log.info("Status: words:%d", len(treemap[label]))
    for w in treemap[label]:
        log.info("  %s: %s: %s: %s", w.LabelName, str(w.Type).ljust(14), str(w.LabelType).ljust(30), str(w.ExplainationRaw)[:50].replace("\n", "\\n"))
        #print(w.Synonymy)
    log.info("Done!")


def mainfunc(lang="en", limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False):
    # prepare:
    #   in: lang
    #      - download
    #      - unpack .bz2
    #      - parse xml
    #      - extract page text
    #   out: text
    #
    # phase 1: (build tree)
    #   in: text
    #     - parse text
    #     - extract templates {{...}}
    #     - extract html <...>
    #     - extract links [[...]]
    #     - extract character data
    #     - create object
    #   out: object tree
    #
    # phase 2: (add sections)
    #   in: object tree
    #      - pack lists
    #      - pack sections
    #   out: object tree
    #
    # phase 3: (data mining)
    #   in: object tree
    #      - scan sections
    #      - scan templates
    #      - scan lists
    #        - detect singular, plural
    #        - detect male, female, neutral
    #        - detect noun, verb, adverb, ...
    #        - detect past, present, futur
    #        - detect translations
    #        - detect synonyms
    #        - detect related
    #        - detect explainations
    #        - detect examples
    #   out: mined tree (mined data grouped by sections)
    #
    # phase 4: (create words)
    #   in: mined tree
    #     - ...
    #   out: words list
    #
    # postprocess: (save words)
    #   in: words list
    #     - save to json
    #     - save to sql
    #
    preprocess(lang, process, limit, is_save_txt, is_save_json, is_save_templates) # next code in process()
