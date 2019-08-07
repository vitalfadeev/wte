#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dbclass import DBClass
from jsonclass import JSONClass
from collections.abc import Iterable
from helpers import remove_comments, extract_from_link
from helpers import filterWodsProblems
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found


class WikictionaryItem(DBClass, JSONClass):
    DB_NAME = "Wikictionary.db"
    DB_TABLE_NAME = "wikictionary"
    DB_PRIMARY = ["PrimaryKey"]
    DB_INDEXES = []


    def __init__(self):
        self.PrimaryKey              = ""
        self.SelfUrl                 = None
        self.LabelName               = ""  #
        self.LabelType               = None  #
        self.LanguageCode            = ""  # (EN,FR,…)
        self.Type                    = ""  # = noun,verb… see = WORD_TYPES
        self.TypeLabelName           = ""  # chatt for verb of chat
        self.ExplainationRaw         = None  #
        self.ExplainationTxt         = None  #
        self.ExplainationExamplesRaw = None
        self.ExplainationExamplesTxt = None
        self.IsMale                  = None
        self.IsFeminine              = None  # ""
        self.IsNeutre                = None  # ""
        self.IsSingle                = None
        self.IsPlural                = None
        self.SingleVariant           = None  # ""
        self.PluralVariant           = None  # ""
        self.PopularityOfWord        =  0
        self.MaleVariant             = None  # ""
        self.FemaleVariant           = None  # ""
        self.IsVerbPast              = None
        self.IsVerbPresent           = None
        self.IsVerbFutur             = None
        self.Conjugation             = []
        self.Synonymy                = []
        self.Antonymy                = []
        self.Hypernymy               = []
        self.Hyponymy                = []
        self.Meronymy                = []
        self.Holonymy                = []
        self.Troponymy               = []
        self.Otherwise               = []
        self.AlternativeFormsOther   = []
        self.RelatedTerms            = []
        self.Coordinate              = []
        self.Translation_EN          = []
        self.Translation_FR          = []
        self.Translation_DE          = []
        self.Translation_IT          = []
        self.Translation_ES          = []
        self.Translation_RU          = []
        self.Translation_PT          = []


    def save_to_json(self, filename):
        save_to_json(self, filename)


    def save_to_pickle(self, filename):
        save_to_pickle(self, filename)


    def add_explaniation(self, raw, txt):
        self.ExplainationRaw = raw
        self.ExplainationTxt = txt

    
    def add_conjugation(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Conjugation is None:
                    self.Conjugation = [ term ]
                else:
                    if term not in self.Conjugation:
                        self.Conjugation.append( term )
    

    def add_synonym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Synonymy is None:
                    self.Synonymy = [ term ]
                else:
                    if term not in self.Synonymy:
                        self.Synonymy.append( term )
    

    def add_antonym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Antonymy is None:
                    self.Antonymy = [ term ]
                else:
                    if term not in self.Antonymy:
                        self.Antonymy.append( term )

    
    def add_hypernym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Hypernymy is None:
                    self.Hypernymy = [ term ]
                else:
                    if term not in self.Hypernymy:
                        self.Hypernymy.append( term )
    

    def add_hyponym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Hyponymy is None:
                    self.Hyponymy = [ term ]
                else:
                    if term not in self.Hyponymy:
                        self.Hyponymy.append( term )
    

    def add_meronym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Meronymy  is None:
                    self.Meronymy = [ term ]
                else:
                    if term not in self.Meronymy:
                        self.Meronymy.append( term )
    

    def add_holonym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Holonymy  is None:
                    self.Holonymy = [ term ]
                else:
                    if term not in self.Holonymy:
                        self.Holonymy.append( term )
    

    def add_troponym(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.Troponymy is None:
                    self.Troponymy = [ term ]
                else:
                    if term not in self.Troponymy:
                        self.Troponymy.append( term )
    

    def add_alternative_form(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.AlternativeFormsOther is None:
                    self.AlternativeFormsOther = [ term ]
                else:
                    if term not in self.AlternativeFormsOther:
                        self.AlternativeFormsOther.append( term )
    

    def add_related(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
                if self.RelatedTerms is None:
                    self.RelatedTerms = [ term ]
                else:
                    if term not in self.RelatedTerms:
                        self.RelatedTerms.append( term )
    

    def add_coordinate(self, lang, term):
        term = filterWodsProblems(term, log)
        if term:
            if term != self.LabelName:
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

        # filter
        term = filterWodsProblems(term, log)

        # storage
        storage_name = storages.get(lang, None)

        # init storage
        storage = getattr(self, storage_name)
        if storage is None:
            # init
            storage = []
            setattr(self, storage_name, storage)

        # append
        if term is None:
            pass
            
        elif isinstance(term, str):
            # one
            if term not in storage:
                storage.append( term )

        elif isinstance(term, Iterable):
            # [list] | (tuple)
            for trm in term:
                if term not in storage:
                    storage.append( term )

        else:
            log.error("unsupported type: %s", type(term))
            # assert 0, "unsupported type"

            
    def clone(self):
        clone = WikictionaryItem()
        
        for name in self.get_fields():
            value = getattr(self, name)
            if isinstance(value, list):
                cloned_value = value.copy()
            else:
                cloned_value = value
            setattr(clone, name, cloned_value)
        
        return clone


    def __repr__(self):
        return "WikictionaryItem(" + self.LabelName + ")"


