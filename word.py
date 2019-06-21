#!/usr/bin/python3
# -*- coding: utf-8 -*-
from dbclass import DBClass
from jsonclass import JSONClass


class Word(DBClass, JSONClass):
    DB_NAME = "Words.db"
    DB_TABLE_NAME = "words"
    DB_PRIMARY = ["PrimaryKey"]
    DB_INDEXES = []

    
    def __init__(self, parent=None):
        self.LabelName                  = None
        self.CodeInWiki                 = None
        self.LanguageCode               = None
        self.Description                = None
        self.AlsoKnownAs                = None
        self.SelfUrl                    = None
        self.WikipediaENURL             = None
        self.EncyclopediaBritannicaEN   = None
        self.EncyclopediaUniversalisEN  = None
        self.Instance_of                = []
        self.Subclass_of                = []
        self.Part_of                    = []
        self.Translation_EN             = []
        self.Translation_FR             = []
        self.Translation_DE             = []
        self.Translation_IT             = []
        self.Translation_ES             = []
        self.Translation_RU             = []
        self.Translation_PT             = []
        #
        self.LabelType                  = None
        self.Type                       = None
        self.Explaination               = None
        self.ExplainationExamples       = []
        self.IsMale                     = None
        self.IsFeminine                 = None
        self.IsSingle                   = None
        self.IsPlural                   = None
        self.SingleVariant              = None
        self.PluralVariant              = None
        self.IsVerbPast                 = None
        self.IsVerbPresent              = None
        self.IsVerbFutur                = None
        self.Conjugation                = []
        self.Synonymy                   = []
        self.Antonymy                   = []
        self.Hypernymy                  = []
        self.Hyponymy	                = []
        self.Meronymy	                = []
        self.Holonymy                   = []
        self.Troponymy                  = []
        self.Otherwise                  = []
        self.AlternativeFormsOther      = []
        self.RelatedTerms               = []
        self.Coordinate                 = []
        #
        self.WikipediaENContent         = None
        self.BritannicaENContent        = None
        self.UniversalisENContent       = None
        
        # inherit from parent
        if parent:
            for f in self.get_fields():
                setattr(self, f, getattr(parent, f))
        

    def __repr__(self):
        return "Word(" + self.LabelName + ")"
