#!/bin/env python3

import os
import bz2
import json
import xml.parsers.expat
import importlib

from blist import sorteddict
from helpers import create_storage, put_contents, get_contents, sanitize_filename
from helpers import load_from_pickle, save_to_pickle, convert_to_alnum, proper, deduplicate
from helpers import remove_comments, extract_from_link
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found
from helpers import is_ascii
import helpers
import wikoo
from wikoo import Section, Template, Link, Li, Mined


TXT_FOLDER      = "txt"     # folder where stored text files for debugging
CACHE_FOLDER    = "cached"  # folder where stored downloadad dumps
WORD_JUST       = 24        # align size
create_storage(TXT_FOLDER)


class KEYS:
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

class Word:
    """
    Main word class.
    Here stored info about word.
    """
    def __init__(self):
        self.LabelName = ""  #
        self.LabelType = None  #
        self.LanguageCode = ""  # (EN,FR,…)
        self.Type = ""  # = noun,verb… see = WORD_TYPES
        self.TypeLabelName = ""  # chatt for verb of chat
        self.ExplainationRaw = None  #
        self.ExplainationTxt = None  #
        self.ExplainationExamplesRaw = None
        self.ExplainationExamplesTxt = None
        self.IsMale = None
        self.IsFeminine= None  # ""
        self.IsSingle = None
        self.IsPlural = None
        self.SingleVariant = None  # ""
        self.PluralVariant = None  # ""
        self.MaleVariant = None  # ""
        self.FemaleVariant = None  # ""
        self.IsVerbPast = None
        self.IsVerbPresent = None
        self.IsVerbFutur = None
        self.Conjugation = None  # [ ] (All verb Conjugation (example = like, liking, liked)
        self.Synonymy = None  # [ ]
        self.Antonymy = None  # [ ]
        self.Hypernymy = None  # [ ]
        self.Hyponymy = None  # [ ]
        self.Meronymy = None  # [ ]
        self.Holonymy = None  # [ ]
        self.Troponymy = None  # [ ]
        self.Otherwise = None  # [ ]
        self.AlternativeFormsOther = None  # [ ]
        self.RelatedTerms = None  # [ ]
        self.Coordinate = None  # [ ]        
        self.Translation_EN = None  # [ ]
        self.Translation_FR = None  # [ ]
        self.Translation_DE = None  # [ ]
        self.Translation_IT = None  # [ ]
        self.Translation_ES = None  # [ ]
        self.Translation_RU = None  # [ ]
        self.Translation_PT = None  # [ ]

    def save_to_json(self, filename):
        save_to_json(self, filename)

    def save_to_pickle(self, filename):
        save_to_pickle(self, filename)

    def add_explaniation(self, raw, txt):
        self.ExplainationRaw = raw
        self.ExplainationTxt = txt
    
    def add_conjugation(self, lang, term):
        if self.Conjugation is None:
            self.Conjugation = [ term ]
        else:
            if term not in self.Conjugation:
                self.Conjugation.append( term )
    
    def add_synonym(self, lang, term):
        if self.Synonymy is None:
            self.Synonymy = [ term ]
        else:
            if term not in self.Synonymy:
                self.Synonymy.append( term )
    
    def add_antonym(self, lang, term):
        if self.Antonymy is None:
            self.Antonymy = [ term ]
        else:
            if term not in self.Antonymy:
                self.Antonymy.append( term )
    
    def add_hypernym(self, lang, term):
        if self.Hypernymy is None:
            self.Hypernymy = [ term ]
        else:
            if term not in self.Hypernymy:
                self.Hypernymy.append( term )
    
    def add_hyponym(self, lang, term):
        if self.Hyponymy is None:
            self.Hyponymy = [ term ]
        else:
            if term not in self.Hyponymy:
                self.Hyponymy.append( term )
    
    def add_meronym(self, lang, term):
        if self.Meronymy  is None:
            self.Meronymy = [ term ]
        else:
            if term not in self.Meronymy:
                self.Meronymy.append( term )
    
    def add_holonym(self, lang, term):
        if self.Holonymy  is None:
            self.Holonymy = [ term ]
        else:
            if term not in self.Holonymy:
                self.Holonymy.append( term )
    
    def add_troponym(self, lang, term):
        if self.Troponymy is None:
            self.Troponymy = [ term ]
        else:
            if term not in self.Troponymy:
                self.Troponymy.append( term )
    
    def add_alternative_form(self, lang, term):
        if self.AlternativeFormsOther is None:
            self.AlternativeFormsOther = [ term ]
        else:
            if term not in self.AlternativeFormsOther:
                self.AlternativeFormsOther.append( term )
    
    def add_related(self, lang, term):
        if self.RelatedTerms is None:
            self.RelatedTerms = [ term ]
        else:
            if term not in self.RelatedTerms:
                self.RelatedTerms.append( term )
    
    def add_coordinate(self, lang, term):
        if self.Coordinate is None:
            self.Coordinate = [ term ]
        else:
            if term not in self.Coordinate:
                self.Coordinate.append( term )
    
    def add_translation(self, lang, term):
        # validate
        if term is None:
            # skip None
            return
            
        term = remove_comments(term)
        term = extract_from_link(term)
        term = term.strip()
        
        if not term:
            # skip blank
            # skip empty
            return

            # prepare
        storages = {
            "en": "Translation_EN",
            "fr": "Translation_FR",
            "de": "Translation_DE",
            "it": "Translation_IT",
            "es": "Translation_ES",
            "ru": "Translation_RU",
            "pt": "Translation_PT",
            #"cn": "Translation_CN",
            #"ja": "Translation_JA"
        }

        # check lang
        if lang not in storages:
            # not supported language
            log.debug("unsupported language: " + str(lang))
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
        if isinstance(term, str):
            # one
            if term not in storage:
                storage.append( term )

        elif isinstance(term, (list, tuple)):
            # [list] | (tuple)
            for trm in term:
                if term not in storage:
                    storage.append( term )

        else:
            log.error("unsupported type: %s", type(term))
            # assert 0, "unsupported type"
            
    def get_fields(self):
        reserved = [
            "sql_table", 'get_fields', 'add_explaniation', 
            'add_related', 'add_synonym', 'add_translation', 'clone', 
            'save_to_json', 'save_to_pickle', "Excpla", "Explainations"
            ]

        result = []
        
        for name in dir(self):
            if callable(name) or name.startswith("_") or name.startswith("add_") or name.startswith("save_"):
                pass # skip
            elif name in reserved:
                pass # skip    
            else:
                result.append(name)
        
        return result
            
    def clone(self):        
        clone = Word()
        
        for name in self.get_fields():
            value = getattr(self, name)
            if isinstance(value, list):
                cloned_value = value.copy()
            else:
                cloned_value = value
            setattr(clone, name, cloned_value)
        
        return clone

    def __repr__(self):
        return "Word(" + self.LabelName + ")"


class WordsEncoder(json.JSONEncoder):
    """
    This class using in JSON encoder.
    Take object with Word objects and return dict.
    """

    def default(self, obj):
        if isinstance(obj, Word):
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

            elif isinstance(storage, Word):
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
            word = Word()

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


def get_label_type(expl):
    list1 = []
    for t in expl.find_objects(Template):
        inner = t.get_text()
        s = convert_to_alnum(inner)
        s = deduplicate(s)
        s = s.strip("_").strip()
        splitted = s.split(" ")
        list1 += [ w.upper() for w in splitted ]

    list2 = []
    for l in expl.find_objects(Link):
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


def preprocess(lang, callback, limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False):
    dump_file = download(lang)
    
    with bz2.open(dump_file, "r") as xml_stream:
        parser = XMLParser()
        parser.parse(xml_stream, callback, lang=lang, limit=limit, is_save_txt=is_save_txt, is_save_json=is_save_json, is_save_templates=is_save_templates) # call process() here


def process(lang, label, text,  limit=0, is_save_txt=False, is_save_json=False, is_save_xml=False, is_save_templates=False):
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

    # process
    tree  = phase1(text)
    tree  = phase2(lang, tree)
    #wikoo.dump(tree, 0, (Section, Li))

    # debug. save tmplates and sections
    if is_save_templates:
        for s in tree.find_objects(Section, recursive=True):
            for t in s.find_objects(Template, recursive=True, exclude=Section):
                helpers.add_template(s, t)
        return  []

    words = phase3(lang, tree, label)
    #words = phase4(lang, mined, label)

    if not words:
        log.warn("no words extracted (%s, %s)... [SKIP]", lang, label)
        return []

    flag  = postprocess(words, label)
    
    return  words


def phase1(text):
    log.debug("phase1()")
    
    tree = wikoo.parse("\n" + text + "\n")
    return tree
    

def phase2(lang, tree):
    log.debug("phase2()")
    lang_module = importlib.import_module(lang)

    tree = wikoo.pack_lists(tree)
    tree = wikoo.pack_sections(tree, lang_module.section_templates)
    return tree


def tscan(lang, section, label):
    # import en, de, fr, ru, ...
    lang_module = importlib.import_module(lang)
    
    # section
    section_rules = lang_module.section_rules
    data = section_rules.get(section.name, None)
    
    if data is not None:
        if isinstance(data, list):
            lst = data
        else:
            lst = [data]
            
        for item in lst:
            if callable(item):
                callback = item
                for (key, value) in callback(section):
                    yield (key, value, repr(section))
            else:
                value = item
                yield (key, value, repr(section))
                
    # templates
    template_rules = lang_module.template_rules

    for t in section.find_objects(Template, recursive=True, exclude=Section):
        data = template_rules.get(t.name, None)
        
        if data is not None:
            if isinstance(data, list):
                lst = data
            else:
                lst = [data]
                
            for item in lst:
                if callable(item):
                    callback = item
                    for (key, value) in callback(t):
                        yield (key, value, repr(t))
                else:
                    value = item
                    yield (key, value, repr(t))
            
        else:
            log_uncatched_template.debug("%s: %s: %s", label, t.name, t.raw.replace("\n", "\\n"))
            
    # explainations
    for li in section.find_objects(Li):
        yield (KEYS.EXPLAIN, li, "explainations")




def try_not_well_formed(tree):
    pass


def phase3(lang, tree, label):
    log.debug("phase3(%s, %s)", lang, label)

    mined = tree
    
    lang_module = importlib.import_module(lang)
    words = lang_module.try_well_formed_structure(tree, label, lang)
    
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
                                word = Word()
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
    flag = None
    if words:
        import sql
        sql.SQLWriteDB( sql.DBWikictionary, {label:words} )
    return flag


def one_file(lang, label):
    """
    Parse only on word 'label'. (For Debugging)

    Get text from the test/<label>.txt
    Save to the test/<label>.json
    """
    log.info("Word: %s", label)
    src_file = os.path.join(TXT_FOLDER, label + ".txt")
    log.info("Loading from: %s", src_file)
    text = get_contents(src_file)

    # parse
    log.info("Parsing")
    words = process(lang, label, text)

    # postprocess
    flag  = postprocess(words, label)

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
        log.info("  %s: %s: %s: %s", w.LabelName, str(w.Type).ljust(14), str(w.LabelType).ljust(64), str(w.ExplainationRaw).replace("\n", "\\n"))
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
