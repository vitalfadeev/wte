#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dbclass import DBClass
from jsonclass import JSONClass


class WikidataItem(DBClass, JSONClass):
    DB_NAME = "WikiData.db"
    DB_TABLE_NAME = "wikidata"
    DB_PRIMARY = ["PrimaryKey"]
    DB_INDEXES = []
    
    
    def __init__(self):
        self.PrimaryKey                 = None
        self.SelfUrl                    = None
        self.LabelName                  = None
        self.LanguageCode               = None
        self.CodeInWiki                 = None
        self.Description                = None
        self.AlsoKnownAs                = []
        self.SelfUrl                    = None
        self.WikipediaENURL             = None
        self.EncyclopediaBritannicaEN   = None
        self.EncyclopediaUniversalisFR  = None
        self.DescriptionUrl             = None
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
        self.WikipediaLinkCountTotal    = None
        self.EncyclopediaGreatRussianRU = None
            

    def __repr__(self):
        return "WikidataItem("+self.LabelName+")"
