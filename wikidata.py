#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dbclass import DBClass
from jsonclass import JSONClass
import inspect


class WikidataItem(DBClass, JSONClass):
    DB_NAME = "WikiData.db"
    DB_TABLE_NAME = "wikidata"
    
    def __init__(self):
        self.LabelName = None
        self.LanguageCode = None
        self.CodeInWiki = None
        self.Description = None
        self.AlsoKnownAs = []
        self.SelfUrl = None
        self.WikipediaENURL = None
        self.EncyclopediaBritannicaEN = None
        self.EncyclopediaUniversalisEN = None
        self.DescriptionUrl = None
        self.Instance_of = []
        self.Subclass_of = []
        self.Part_of = []
        self.Translation_EN = []
        self.Translation_FR = []
        self.Translation_DE = []
        self.Translation_IT = []
        self.Translation_ES = []
        self.Translation_RU = []
        self.Translation_PT = []
 

    def get_fields(self):
        reserved = [ "DB_NAME", "DB_TABLE_NAME", "Excpla", "Explainations" ]

        result = []
        
        for name in dir(self):
            if callable(getattr(self, name)):
                pass # skip
            elif inspect.ismethod(getattr(self, name)):
                pass # skip
            elif name.startswith("_"):
                pass # skip
            elif name in reserved:
                pass # skip    
            else:
                result.append(name)
        
        return result
            

    def __repr__(self):
        return "WikidataItem("+self.LabelName+")"
