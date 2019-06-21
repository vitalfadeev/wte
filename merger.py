#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os.path
import json
import sqlite3
import requests
import wikipedia
from wikidata import WikidataItem as WikidataItemClass
from wiktionary import WikictionaryItem as WikictionaryItemClass
from sql import DBWikiData, DBWikictionary, get_new_id
from word import Word
from dbclass import from_db
from helpers import get_contents, put_contents, unique


#DBWords = sqlite3.connect("Words.db")


class CacheRequest:
    """ decorator """    

    def __init__(self, function): 
        self._cache = {}
        self.function = function 


    def __call__(self, url, *args, **kwarg):
        # reset cache for memory keeping
        if len(self._cache) > 1000:
            self._cache = {}

        #
        if url in self._cache:
            return self._cache[url]
        else:
            data = self.function(url, *args, **kwarg)
            self._cache[url] = data
            return data


class DescriptionItem():
    def __init__(self):
        self.URL = None
        self.TITLE = None
        self.CONTENT = None


class WikipediaDescriptionItem(DescriptionItem):
    None


class BritannicaDescriptionItem(DescriptionItem):
    None


class UniversalisDescriptionItem(DescriptionItem):
    None


def SQLInit():
    """ Create tables """
    sql = """
    CREATE TABLE IF NOT EXISTS words (
        id              BIGINT,
        LabelName       text,
        CodeInWiki      text,
        LanguageCode    text,
        Description     text,
        AlsoKnownAs     text,
        SelfUrl         text,
        WikipediaENURL  text,
        EncyclopediaBritannicaEN text,
        EncyclopediaUniversalisEN text,
        Instance_of     text,
        Subclass_of     text,
        Part_of         text,
        Translation_EN  text,    
        Translation_FR  text,
        Translation_DE  text,
        Translation_IT  text,
        Translation_ES  text,
        Translation_RU  text,
        Translation_PT  text,
        
        LabelType       text,
        Type            text,
        Explaination    text,
        ExplainationExamples text,
        IsMale          text,
        IsFeminine      text,
        IsSingle        text,
        IsPlural        text,
        SingleVariant   text,
        PluralVariant   text,
        IsVerbPast      text,
        IsVerbPresent   text,
        IsVerbFutur     text,
        Conjugation     text,
        Synonymy        text,
        Antonymy        text,
        Hypernymy       text,
        Hyponymy	    text,
        Meronymy	    text,
        Holonymy        text,
        Troponymy       text,
        Otherwise       text,
        AlternativeFormsOther text,
        RelatedTerms    text,
        Coordinate      text,
        
        WikipediaENContent   text,
        BritannicaENContent  text,
        UniversalisENContent text
    ) 
    """
    c = DBWords.cursor()
    c.execute(sql)
    
    
    # DescriptionItem
    sql = """
    CREATE TABLE IF NOT EXISTS DescriptionItem (
        id          BIGINT,
        URL         text,
        TITLE       text,
        CONTENT     text
    ) 
    """
    c = DBWords.cursor()
    c.execute(sql)


def SearchWikictionary( WikidataItem ):
    yield from from_db(WikictionaryItemClass, LabelName = WikidataItem.LabelName )


def CompareWikictionary(WikidataItem, WikictionaryItem):
    if WikidataItem.LabelName == WikictionaryItem.LabelName:
        if WikidataItem.LanguageCode == WikictionaryItem.LanguageCode:
            return True


def MergeWikidata( word, WikidataItem ):
    word = Word(word)
    word.PrimaryKey                 = WikidataItem.PrimaryKey
    word.LabelName                  = WikidataItem.LabelName
    word.CodeInWiki                 = WikidataItem.CodeInWiki
    word.LanguageCode               = WikidataItem.LanguageCode
    word.DescriptionWikiData        = WikidataItem.Description # DescriptionWikiData
    word.AlsoKnownAs                = WikidataItem.AlsoKnownAs
    word.WikiDataUrl                = WikidataItem.SelfUrl # WikiDataUrl
    word.WikipediaENURL             = WikidataItem.WikipediaENURL
    word.EncyclopediaBritannicaEN   = WikidataItem.EncyclopediaBritannicaEN
    word.EncyclopediaUniversalisEN  = WikidataItem.EncyclopediaUniversalisEN
    word.Instance_of                = WikidataItem.Instance_of
    word.Subclass_of                = WikidataItem.Subclass_of
    word.Part_of                    = WikidataItem.Part_of
    word.Translation_EN             = WikidataItem.Translation_EN
    word.Translation_FR             = WikidataItem.Translation_FR
    word.Translation_DE             = WikidataItem.Translation_DE
    word.Translation_IT             = WikidataItem.Translation_IT
    word.Translation_ES             = WikidataItem.Translation_ES
    word.Translation_RU             = WikidataItem.Translation_RU
    word.Translation_PT             = WikidataItem.Translation_PT
    
    return word
    

def MergeWiktionary( word, WikictionaryItem ):
    word = Word(word)
    word.Type                       = WikictionaryItem.Type
    word.LabelType                  = WikictionaryItem.LabelType
    word.ExplainationWiktionary     = WikictionaryItem.ExplainationRaw
    word.ExamplesWiktionary         = WikictionaryItem.ExplainationExamplesRaw
    word.IsMale                     = WikictionaryItem.IsMale
    word.IsFeminine                 = WikictionaryItem.IsFeminine
    word.IsSingle                   = WikictionaryItem.IsSingle
    word.IsPlural                   = WikictionaryItem.IsPlural
    word.SingleVariant              = WikictionaryItem.SingleVariant
    word.PluralVariant              = WikictionaryItem.PluralVariant
    word.IsVerbPast                 = WikictionaryItem.IsVerbPast
    word.IsVerbPresent              = WikictionaryItem.IsVerbPresent
    word.IsVerbFutur                = WikictionaryItem.IsVerbFutur
    word.Conjugation                = WikictionaryItem.Conjugation
    word.Translation_EN             += WikictionaryItem.Translation_EN
    word.Translation_FR             += WikictionaryItem.Translation_FR
    word.Translation_DE             += WikictionaryItem.Translation_DE
    word.Translation_IT             += WikictionaryItem.Translation_IT
    word.Translation_ES             += WikictionaryItem.Translation_ES
    word.Translation_RU             += WikictionaryItem.Translation_RU
    word.Translation_PT             += WikictionaryItem.Translation_PT
    word.Synonymy                   = WikictionaryItem.Synonymy
    word.Antonymy                   = WikictionaryItem.Antonymy
    word.Hypernymy                  = WikictionaryItem.Hypernymy
    word.Hyponymy	                = WikictionaryItem.Hyponymy	
    word.Meronymy	                = WikictionaryItem.Meronymy
    word.Holonymy                   = WikictionaryItem.Holonymy
    word.Troponymy                  = WikictionaryItem.Troponymy
    word.Otherwise                  = WikictionaryItem.Otherwise
    word.AlternativeFormsOther      = WikictionaryItem.AlternativeFormsOther
    word.RelatedTerms               = WikictionaryItem.RelatedTerms
    word.Coordinate                 = WikictionaryItem.Coordinate
    
    word.Translation_EN = unique(word.Translation_EN)
    word.Translation_FR = unique(word.Translation_FR)
    word.Translation_DE = unique(word.Translation_DE)
    word.Translation_IT = unique(word.Translation_IT)
    word.Translation_ES = unique(word.Translation_ES)
    word.Translation_RU = unique(word.Translation_RU)
    word.Translation_PT = unique(word.Translation_PT)
    
    return word


def MergeContent( word, DescriptionItem ):
    word = Word(word)
    
    if isinstance(DescriptionItem, WikipediaDescriptionItem):
        word.WikipediaENContent     = DescriptionItem.TITLE + "\n" + DescriptionItem.CONTENT
        return word
        
    if isinstance(DescriptionItem, BritannicaDescriptionItem):
        word.BritannicaENContent    = DescriptionItem.TITLE + "\n" + DescriptionItem.CONTENT
        return word
        
    if isinstance(DescriptionItem, UniversalisDescriptionItem):
        word.UniversalisENContent   = DescriptionItem.TITLE + "\n" + DescriptionItem.CONTENT
        return word
    
    return word
    
    
# AlsoKnownAs
# ExplainationWiktionary
# ExamplesWiktionary

# DescriptionItem
#   URL
#   TITLE
#   CONTENT


@CacheRequest
def GetContentWikipedia( Url, WikidataItem ):
    wikipedia.set_lang("en")
    
    # defined url
    url = WikidataItem.WikipediaENURL
    
    if url:
        pass
    else:
        # build url
        url = "" + WikidataItem.LabelName
    
    page = wikipedia.page( WikidataItem.LabelName )

    desc = WikipediaDescriptionItem()
    desc.URL = page.url
    desc.TITLE = page.title
    desc.CONTENT = page.content    
    
    return desc


@CacheRequest
def GetContentBritanica( Url, WikidataItem ):
    html_doc = requests.get(Url).text

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    desc = BritannicaDescriptionItem()
    desc.URL = Url
    desc.TITLE = soup.title.get_text()
    content = soup.find("article", id="article-content") # <article id="article-content" class="content">
    if content is None:
        content = soup.find("section", id="corps-fr") # <section class="col-sm-8 col-lg-9" id="corps-fr">
    desc.CONTENT = content.get_text() if content else ""
    
    return desc


@CacheRequest
def GetContentUniversalis( Url, WikidataItem ):
    html_doc = requests.get(Url).text

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    desc = UniversalisDescriptionItem()
    desc.URL = Url
    desc.TITLE = soup.title.get_text()
    content = soup.find("section", id="corps-fr")
    desc.CONTENT = content.get_text() if content else ""
    
    return desc
    

def CompareContent ( Word, DescriptionItem ):
    pass
    

def wikidata_reader():
    yield from from_db(WikidataItemClass)
    
    

class SavePoint:
    point = None
    POINT_FILE_NAME = "savepoint.txt"
    _must_check = False

    @classmethod
    def check_save_point(self, s):
        if self._must_check:
            if self.point == s:
                return True
            else:
                return False
        else:
            return True


    @classmethod
    def load_save_point(self):
        if os.path.isfile(self.POINT_FILE_NAME):
            self.point = get_contents(self.POINT_FILE_NAME)
            if self.point:
                print("Savepoint found:", self.POINT_FILE_NAME, ":", self.point)
                self._must_check = True


    @classmethod
    def make_save_point(self, s):
        put_contents(self.POINT_FILE_NAME, s)
        self._must_check = False


def mainfunc():
    SavePoint.load_save_point()
    
    WikictionaryItemClass().create_index(LabelName=1)

    # read words from wikidata
    for WikidataItem in wikidata_reader():
        if SavePoint.check_save_point( str(WikidataItem.id) ):
            pass # savepoint found or first run
        else:
            continue # skip. because waiting savepoint

        print( WikidataItem )

        SavePoint.make_save_point( str(WikidataItem.id) )

        # header
        for s in ["WD", "WT", "Wp", "Br", "Un", "Done"]:
            print( s.ljust(3), end="" )
        print()

        # WD
        print('*'.ljust(3), end="")
        
        if 0:
            if WikidataItem.LabelName == "Belgique":
                pass
            else:
                continue
            
        word = Word()        
        word = MergeWikidata( word, WikidataItem )

        # search Wiktionary
        words = []
        for WikictionaryItem in SearchWikictionary( WikidataItem ):
            if CompareWikictionary ( WikidataItem, WikictionaryItem ):
                word = MergeWiktionary( word, WikictionaryItem )
                words.append(word)

        # words
        if len(words) > 0:
            # WT
            print((str(len(words))).ljust(3), end="")
            sys.stdout.flush()
            
        else:
            words.append(word)
            # WT
            print(('.').ljust(3), end="")
            sys.stdout.flush()
            
        
        # descriptions
        words2 = []
        for word in words:
            # WP
            Url = word.WikipediaENURL
            WP_found = ""
            if Url:
                try:
                    DescriptionItem = GetContentWikipedia( Url, WikidataItem )
                    word = MergeContent(word, DescriptionItem)
                    if len(DescriptionItem.CONTENT) > 0:
                        WP_found = "*"
                except wikipedia.exceptions.DisambiguationError:
                    WP_found = "E"
                except wikipedia.exceptions.PageError:
                    WP_found = "E"
                except wikipedia.exceptions:
                    WP_found = "E"
                    
            if WP_found:
                print(WP_found.ljust(3), end="")
                sys.stdout.flush()
            else:
                print('.'.ljust(3), end="")
                sys.stdout.flush()


            # BR
            Url = word.EncyclopediaBritannicaEN
            BR_found = False
            if Url:
                DescriptionItem = GetContentBritanica( Url, WikidataItem )
                word = MergeContent(word, DescriptionItem)
                BR_found = True

            if BR_found:
                print('*'.ljust(3), end="")
                sys.stdout.flush()
            else:
                print('.'.ljust(3), end="")
                sys.stdout.flush()


            # UN
            Url = word.EncyclopediaUniversalisEN
            UN_found = False
            if Url:
                DescriptionItem = GetContentUniversalis( Url, WikidataItem )
                word = MergeContent(word, DescriptionItem)
                UN_found = True

            # UN
            if UN_found:
                print('*'.ljust(3), end="")
                sys.stdout.flush()
            else:
                print('.'.ljust(3), end="")
                sys.stdout.flush()

            words2.append(word)
            
            # stub eol for logging
            if len(words) > 1 and len(words) != len(words2):
                print()
                print(" " * (3 * len(["WD", "WT"])), end="")
            
        if words2:
            words = words2
            
        # write words
        for word in words:
            word.save_to_db()

        # Done
        print( '*'.ljust(3) )
    

def test():
    word = Word()
    word.LabelName = "Cat"
    
    #DescriptionItem = GetContentWikipedia("", word)
    
    #Url = "https://www.britannica.com/animal/" + word.LabelName
    #DescriptionItem = GetContentBritanica(Url, word) # How to fetch content from Britanica? It require registrations, and credit card number. https://www.britannica.com/animal/cat
    
    Url = "https://www.universalis.fr/encyclopedie/chat-domestique/"
    DescriptionItem = GetContentUniversalis(Url, word)
    
    print(DescriptionItem.TITLE)
    #print(DescriptionItem.CONTENT)

